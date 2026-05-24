"""
Creative Strategy Agent
Generates creative directions for marketing campaigns
"""
import hashlib
import logging
from typing import Dict, List, Optional

from groq import Groq

import config
from agents.groq_utils import groq_chat, parse_json_object

logger = logging.getLogger(__name__)

STRATEGY_SYSTEM = """You are a senior performance marketing strategist at a top e-commerce agency.
Every strategy MUST be unique to the specific product provided.
Never reuse generic hooks, palettes, or audiences across different products.
Base every recommendation on the actual product title, description, features, price, and category.
Output valid JSON only — no markdown, no explanation outside JSON."""


class CreativeStrategyAgent:
    """Generates creative strategy and marketing angles from product data"""

    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key) if groq_api_key else None
        self.model = config.GROQ_MODEL

    def generate_strategy(
        self,
        product_data: Dict,
        brand_override: str = None,
        target_audience: str = None,
        custom_themes: Optional[List[str]] = None,
    ) -> Dict:
        title = product_data.get("title", "Product")
        logger.info(f"Generating creative strategy for: {title}")

        if not self.client:
            return self._product_aware_fallback(product_data, target_audience, custom_themes, "no_api_key")

        brand = brand_override or product_data.get("brand", "the brand")
        prompt = self._build_strategy_prompt(product_data, brand, target_audience, custom_themes)

        text = groq_chat(
            self.client, self.model, prompt,
            temperature=0.85, max_tokens=2000, system=STRATEGY_SYSTEM,
        )

        if text:
            strategy = self._parse_strategy_response(text, product_data, target_audience, custom_themes)
            if strategy:
                strategy["source"] = "llm"
                strategy["product_title"] = title
                logger.info(f"✓ LLM strategy generated for: {title}")
                return strategy

        logger.warning(f"Strategy LLM failed for {title} — using product-aware fallback")
        return self._product_aware_fallback(product_data, target_audience, custom_themes, "llm_failed")

    def _build_strategy_prompt(
        self,
        product_data: Dict,
        brand: str,
        target_audience: str = None,
        custom_themes: Optional[List[str]] = None,
    ) -> str:
        title = product_data.get("title", "Product")
        description = product_data.get("description", "")
        short = product_data.get("short_summary", "")
        category = product_data.get("category", "unknown category")
        features = ", ".join(product_data.get("features", [])[:10])
        specs = ", ".join(f"{k}: {v}" for k, v in list(product_data.get("specs", {}).items())[:6])
        price = product_data.get("price")
        currency = product_data.get("currency", "USD")
        rating = product_data.get("rating")
        reviews = product_data.get("reviews_summary", "")
        url = product_data.get("url", "")

        audience_line = f"Target audience override: {target_audience}" if target_audience else ""
        themes_line = f"Required themes: {', '.join(custom_themes)}" if custom_themes else ""

        return f"""Create a UNIQUE marketing strategy for this ONE product only.

PRODUCT URL: {url}
PRODUCT: {title}
BRAND: {brand}
CATEGORY: {category}
DESCRIPTION: {description}
SUMMARY: {short}
FEATURES: {features or 'N/A'}
SPECS: {specs or 'N/A'}
PRICE: {currency} {price if price else 'N/A'}
RATING: {f'{rating}/5' if rating else 'Not rated'}
REVIEWS: {reviews or 'N/A'}
{audience_line}
{themes_line}

Requirements:
- All 5 hooks must mention or clearly reference "{title}" or its core benefit
- Target audience must be specific buyers of THIS product type (not "young professionals" generically)
- Visual themes must match THIS product's category and aesthetics
- Color palette must suit THIS product (e.g. tech=sleek dark tones, skincare=soft pastels, sports=bold colors)
- Marketing angles must cite real features from the data above
- Ad captions must name or describe "{title}" specifically

Return JSON:
{{
  "hooks": ["5 unique hooks for {title}"],
  "target_audience": "specific buyer persona for {title}",
  "visual_themes": ["3 themes matching {title}"],
  "color_palette": ["4 colors suited to {title}"],
  "marketing_angles": ["3 angles based on real features"],
  "ad_captions": ["3 captions mentioning {title}"],
  "tone_of_voice": "tone matching {title} brand and price point"
}}"""

    def _parse_strategy_response(
        self,
        response_text: str,
        product_data: Dict,
        target_audience: str = None,
        custom_themes: Optional[List[str]] = None,
    ) -> Optional[Dict]:
        parsed = parse_json_object(response_text)
        if not parsed:
            return None

        visual_themes = parsed.get("visual_themes", [])
        if custom_themes:
            visual_themes = list(dict.fromkeys(custom_themes + visual_themes))

        hooks = parsed.get("hooks", [])
        if not hooks or len(hooks) < 3:
            return None

        return {
            "hooks": hooks[:5],
            "target_audience": target_audience or parsed.get("target_audience", ""),
            "visual_themes": visual_themes[:5],
            "color_palette": parsed.get("color_palette", [])[:6],
            "marketing_angles": parsed.get("marketing_angles", [])[:5],
            "ad_captions": parsed.get("ad_captions", [])[:5],
            "tone_of_voice": parsed.get("tone_of_voice", ""),
            "product_title": product_data.get("title", ""),
        }

    def _product_aware_fallback(
        self,
        product_data: Dict,
        target_audience: str = None,
        custom_themes: Optional[List[str]] = None,
        reason: str = "",
    ) -> Dict:
        """Fallback that still varies by product — never identical across URLs."""
        title = product_data.get("title", "this product")
        category = product_data.get("category", "")
        features = product_data.get("features", [])[:3]
        brand = product_data.get("brand", "")
        price = product_data.get("price") or 0

        seed = int(hashlib.md5(title.encode()).hexdigest(), 16)
        palettes = [
            ["#1a1a2e", "#16213e", "#e94560", "#ffffff"],
            ["#2d3436", "#636e72", "#00b894", "#fdcb6e"],
            ["#fdf6ec", "#e17055", "#d63031", "#2d3436"],
            ["#0c0c0c", "#c9a96e", "#f5f5f5", "#8b7355"],
            ["#1e3799", "#4a69bd", "#f6b93b", "#ffffff"],
        ]
        themes_pool = [
            ["Studio hero shots", "Lifestyle in-use", "Macro detail close-ups"],
            ["Outdoor action context", "Bold color blocking", "Dynamic angles"],
            ["Minimal clean backdrop", "Soft natural light", "Premium unboxing"],
            ["Urban lifestyle", "Social proof UGC style", "Before/after narrative"],
        ]

        palette = palettes[seed % len(palettes)]
        themes = custom_themes or themes_pool[seed % len(themes_pool)]
        feat_text = features[0] if features else "standout quality"

        return {
            "hooks": [
                f"Stop scrolling — {title} is worth your attention",
                f"The {feat_text} you've been searching for? It's {title}",
                f"Why {title} has {product_data.get('rating', '5')}-star buyers obsessed" if product_data.get("rating") else f"Meet {title} — built different",
                f"{brand + ' ' if brand and brand != 'Unknown Brand' else ''}{title}: premium at {product_data.get('currency', 'USD')} {price}" if price else f"Discover what makes {title} special",
                f"POV: you finally found {title}",
            ],
            "target_audience": target_audience or f"Buyers shopping for {category or title} in the {('premium' if price > 100 else 'value')} segment",
            "visual_themes": themes,
            "color_palette": palette,
            "marketing_angles": [
                f"{title} delivers {feat_text}",
                f"Top-rated {category or 'product'} at {'premium' if price > 100 else 'accessible'} pricing",
                f"Real features buyers love: {', '.join(features[:2]) or 'quality and design'}",
            ],
            "ad_captions": [
                f"Just got my {title} — obsessed ✨",
                f"{title} > everything else in this category",
                f"Link in bio before {title} sells out",
            ],
            "tone_of_voice": "Premium and aspirational" if price > 100 else "Friendly, energetic, and relatable",
            "source": f"fallback_{reason}",
            "product_title": title,
        }


creative_strategy_agent = None
