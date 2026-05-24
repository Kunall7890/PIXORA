"""
Critic/Review Agent
Evaluates generated creatives for quality, consistency, and hallucinations
"""
import hashlib
import logging
from typing import Dict, List, Tuple

from groq import Groq

import config
from agents.groq_utils import groq_chat, parse_json_object

logger = logging.getLogger(__name__)

CRITIC_SYSTEM = """You are a senior creative QA director reviewing marketing assets for a specific product.
Scores MUST reflect how well the creatives match THIS product's actual facts and strategy.
Different products must receive different scores based on their content quality and accuracy.
Output valid JSON only."""


class CriticAgent:
    """Reviews and evaluates generated creatives"""

    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key) if groq_api_key else None
        self.model = config.GROQ_MODEL

    def review_creatives(
        self,
        product_data: Dict,
        creative_brief: Dict,
        image_prompts: List[str],
        video_scripts: List[str],
    ) -> Dict:
        title = product_data.get("title", "")
        logger.info(f"Reviewing creatives for: {title}")

        if self.client:
            result = self._llm_review(product_data, creative_brief, image_prompts, video_scripts)
            if result:
                result["product_title"] = title
                result["source"] = "llm"
                logger.info(f"✓ LLM review for {title}: {result['overall_quality']:.2f}")
                return result

        logger.warning(f"Using heuristic review for: {title}")
        return self._heuristic_review(product_data, creative_brief, image_prompts, video_scripts)

    def _llm_review(
        self,
        product_data: Dict,
        creative_brief: Dict,
        image_prompts: List[str],
        video_scripts: List[str],
    ) -> Dict:
        title = product_data.get("title", "")
        description = product_data.get("description", "")[:400]
        features = ", ".join(product_data.get("features", [])[:8])
        brand = product_data.get("brand", "")
        all_prompts = "\n---\n".join(image_prompts + video_scripts)

        prompt = f"""Review these marketing creatives for product: "{title}"

PRODUCT FACTS:
- Brand: {brand}
- Description: {description}
- Features: {features}
- Price: {product_data.get('currency', 'USD')} {product_data.get('price', 'N/A')}

CREATIVE STRATEGY:
- Audience: {creative_brief.get('target_audience', '')}
- Themes: {', '.join(creative_brief.get('visual_themes', []))}
- Tone: {creative_brief.get('tone_of_voice', '')}
- Hooks: {', '.join(creative_brief.get('hooks', [])[:3])}

GENERATED PROMPTS & SCRIPTS:
{all_prompts}

Score each dimension 0.0 to 1.0 for THIS product specifically:
- hallucination_score: factual accuracy (no false claims about {title})
- consistency_score: alignment with the creative strategy above
- branding_score: brand voice and audience fit for {title}

Also provide product-specific issues and suggestions.

Return JSON:
{{
  "hallucination_score": 0.0,
  "consistency_score": 0.0,
  "branding_score": 0.0,
  "issues": ["specific issue about {title} creatives"],
  "suggestions": ["specific improvement for {title}"]
}}"""

        text = groq_chat(
            self.client, self.model, prompt,
            temperature=0.2, max_tokens=800, system=CRITIC_SYSTEM,
        )
        parsed = parse_json_object(text)
        if not parsed:
            return None

        h = float(parsed.get("hallucination_score", 0.5))
        c = float(parsed.get("consistency_score", 0.5))
        b = float(parsed.get("branding_score", 0.5))
        h, c, b = [min(max(s, 0), 1) for s in (h, c, b)]
        overall = (h + c + b) / 3

        return {
            "hallucination_score": h,
            "consistency_score": c,
            "branding_score": b,
            "overall_quality": overall,
            "issues": parsed.get("issues", []),
            "suggestions": parsed.get("suggestions", []),
            "approved": (
                h >= config.HALLUCINATION_THRESHOLD
                and c >= config.CONSISTENCY_THRESHOLD
                and b >= config.BRANDING_THRESHOLD
            ),
        }

    def _heuristic_review(
        self,
        product_data: Dict,
        creative_brief: Dict,
        image_prompts: List[str],
        video_scripts: List[str],
    ) -> Dict:
        """Product-varying scores when LLM is unavailable."""
        title = product_data.get("title", "").lower()
        brand = product_data.get("brand", "").lower()
        features = product_data.get("features", [])
        all_text = " ".join(image_prompts + video_scripts).lower()

        seed = int(hashlib.md5(title.encode()).hexdigest(), 16)

        # Accuracy: does generated content mention the product?
        title_words = [w for w in title.split() if len(w) > 3]
        title_mentions = sum(1 for w in title_words if w in all_text)
        hallucination = min(0.95, 0.55 + (title_mentions / max(len(title_words), 1)) * 0.35)

        # Consistency: do themes appear in prompts?
        themes = creative_brief.get("visual_themes", [])
        theme_hits = sum(1 for t in themes if any(w in all_text for w in t.lower().split()[:2]))
        consistency = min(0.95, 0.50 + (theme_hits / max(len(themes), 1)) * 0.40)

        # Branding: brand or product name in content
        branding = 0.60
        if brand and brand != "unknown brand" and brand in all_text:
            branding += 0.15
        if title and any(w in all_text for w in title_words):
            branding += 0.15
        branding = min(0.92, branding + (seed % 10) / 100)

        overall = (hallucination + consistency + branding) / 3
        issues, suggestions = self._identify_issues(
            product_data, creative_brief, hallucination, consistency, branding
        )

        return {
            "hallucination_score": round(hallucination, 2),
            "consistency_score": round(consistency, 2),
            "branding_score": round(branding, 2),
            "overall_quality": round(overall, 2),
            "issues": issues,
            "suggestions": suggestions,
            "approved": overall >= 0.72,
            "product_title": product_data.get("title", ""),
            "source": "heuristic",
        }

    def _identify_issues(
        self,
        product_data: Dict,
        creative_brief: Dict,
        hallucination: float,
        consistency: float,
        branding: float,
    ) -> Tuple[List[str], List[str]]:
        issues = []
        suggestions = []
        title = product_data.get("title", "product")

        if hallucination < config.HALLUCINATION_THRESHOLD:
            issues.append(f"Creatives for '{title}' may contain inaccurate product claims")
            suggestions.append(f"Ensure prompts only reference verified features of {title}")

        if consistency < config.CONSISTENCY_THRESHOLD:
            issues.append(f"Visual prompts for '{title}' don't fully match the creative strategy")
            suggestions.append(f"Align image prompts with themes: {', '.join(creative_brief.get('visual_themes', [])[:2])}")

        if branding < config.BRANDING_THRESHOLD:
            issues.append(f"Brand voice for '{title}' is weak in generated scripts")
            suggestions.append(f"Include '{title}' and '{product_data.get('brand', '')}' more prominently")

        if not issues:
            suggestions.append(f"Creatives for '{title}' are well-aligned with product data")

        return issues, suggestions


critic_agent = None
