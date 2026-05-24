"""
Prompt Generation Agent
Creates optimized prompts for image and video generation models
"""
import logging
from typing import Dict, List, Optional
from groq import Groq
import config
from agents.groq_utils import groq_chat, parse_json_array

logger = logging.getLogger(__name__)


class PromptGenerationAgent:
    """Generates optimized prompts for SDXL and video models"""

    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key) if groq_api_key else None
        self.model = config.GROQ_MODEL

    def generate_prompts(
        self,
        product_data: Dict,
        creative_brief: Dict,
        custom_themes: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate optimized image and video prompts

        Returns:
            Dict with image_prompts, video_scripts, visual_style_guide
        """
        try:
            logger.info(f"Generating prompts for: {product_data.get('title')}")

            image_prompts = self._generate_image_prompts(
                product_data, creative_brief, custom_themes
            )
            video_scripts = self._generate_video_scripts(product_data, creative_brief)
            style_guide = self._generate_style_guide(product_data, creative_brief)

            logger.info("✓ Prompts generated successfully")
            return {
                "image_prompts": image_prompts,
                "video_scripts": video_scripts,
                "visual_style_guide": style_guide,
                "source": "llm",
            }

        except Exception as e:
            logger.error(f"Error generating prompts: {str(e)}")
            return {**self._default_prompts(product_data), "source": "default"}

    def _product_context(self, product_data: Dict) -> str:
        """Build rich product context string for LLM prompts."""
        title = product_data.get("title", "Product")
        description = product_data.get("description", "")
        short = product_data.get("short_summary", "")
        category = product_data.get("category", "")
        features = ", ".join(product_data.get("features", [])[:8])
        specs = ", ".join(
            f"{k}: {v}" for k, v in list(product_data.get("specs", {}).items())[:5]
        )
        brand = product_data.get("brand", "")
        price = product_data.get("price")
        currency = product_data.get("currency", "USD")
        rating = product_data.get("rating")
        reviews = product_data.get("reviews_summary", "")

        price_str = f"{currency} {price}" if price else "N/A"
        rating_str = f"{rating}/5" if rating else "Not rated"

        return f"""PRODUCT: {title}
BRAND: {brand}
CATEGORY: {category or 'N/A'}
DESCRIPTION: {description}
SUMMARY: {short or 'N/A'}
KEY FEATURES: {features or 'N/A'}
SPECS: {specs or 'N/A'}
PRICE: {price_str}
RATING: {rating_str}
CUSTOMER REVIEWS: {reviews[:300] if reviews else 'N/A'}"""

    def _generate_image_prompts(
        self,
        product_data: Dict,
        creative_brief: Dict,
        custom_themes: Optional[List[str]] = None,
    ) -> List[str]:
        """Generate 5 varied image prompts for SDXL"""
        try:
            title = product_data.get("title", "Product")
            themes = creative_brief.get("visual_themes", [])
            if custom_themes:
                themes = list(dict.fromkeys(custom_themes + themes))
            colors = creative_brief.get("color_palette", [])
            tone = creative_brief.get("tone_of_voice", "")
            angles = creative_brief.get("marketing_angles", [])

            prompt = f"""You are an expert prompt engineer for Stable Diffusion XL.
Generate 5 DIFFERENT high-quality image prompts for marketing photography of THIS SPECIFIC PRODUCT.

{self._product_context(product_data)}

CREATIVE DIRECTION:
- Visual Themes: {', '.join(themes)}
- Color Palette: {', '.join(colors)}
- Tone: {tone}
- Marketing Angles: {', '.join(angles[:3])}

Create 5 UNIQUE prompts for "{title}" product photography. Each prompt MUST:
- Reference the actual product name "{title}" and its key features
- Be detailed and specific (50-100 words each)
- Include lighting, composition, and mood matching the brand
- Focus on product showcase with lifestyle context
- Include photography style (e.g., "studio shot", "lifestyle photography")
- Specify color grading and atmosphere from the palette

Return as JSON array of 5 strings, nothing else:
["prompt1", "prompt2", "prompt3", "prompt4", "prompt5"]"""

            text = groq_chat(self.client, self.model, prompt, temperature=0.8, max_tokens=2000)
            if not text:
                return self._default_image_prompts(product_data)

            prompts = parse_json_array(text)
            if len(prompts) < 5:
                defaults = self._default_image_prompts(product_data)
                prompts.extend(defaults[: 5 - len(prompts)])

            return prompts[:5]

        except Exception as e:
            logger.error(f"Error generating image prompts: {str(e)}")
            return self._default_image_prompts(product_data)

    def _generate_video_scripts(self, product_data: Dict, creative_brief: Dict) -> List[str]:
        """Generate 2 video scripts for short-form video generation"""
        try:
            title = product_data.get("title", "Product")
            hooks = creative_brief.get("hooks", [])
            captions = creative_brief.get("ad_captions", [])
            audience = creative_brief.get("target_audience", "")

            prompt = f"""You are an expert video copywriter for short-form content (TikTok, Reels, Shorts).
Generate 2 DIFFERENT video scripts for 8-15 second product marketing videos for THIS SPECIFIC PRODUCT.

{self._product_context(product_data)}

CREATIVE DIRECTION:
- Target Audience: {audience}
- Hooks: {', '.join(hooks[:3])}
- Captions: {', '.join(captions[:3])}

Each script MUST:
- Mention "{title}" by name at least once
- Be 8-15 seconds when read at normal pace
- Start with an attention-grabbing hook specific to this product
- Include product showcase moment highlighting real features
- End with call-to-action
- Include [VISUAL: ...] descriptions for key moments

Return as JSON array of 2 strings:
["script1", "script2"]"""

            text = groq_chat(self.client, self.model, prompt, temperature=0.8, max_tokens=2000)
            if not text:
                return self._default_video_scripts(product_data)

            scripts = parse_json_array(text)
            if len(scripts) < 2:
                defaults = self._default_video_scripts(product_data)
                scripts.extend(defaults[: 2 - len(scripts)])

            return scripts[:2]

        except Exception as e:
            logger.error(f"Error generating video scripts: {str(e)}")
            return self._default_video_scripts(product_data)

    def _generate_style_guide(self, product_data: Dict, creative_brief: Dict) -> str:
        """Generate visual style guide for consistency"""
        try:
            title = product_data.get("title", "Product")
            themes = creative_brief.get("visual_themes", [])
            colors = creative_brief.get("color_palette", [])
            tone = creative_brief.get("tone_of_voice", "")

            prompt = f"""You are a creative director. Generate a concise visual style guide for marketing "{title}".

{self._product_context(product_data)}

VISUAL THEMES: {', '.join(themes)}
COLOR PALETTE: {', '.join(colors)}
TONE: {tone}

Create a style guide covering:
1. Overall aesthetic for this specific product (1-2 sentences)
2. Photography style and mood
3. Color usage guidelines
4. Composition principles
5. Lighting approach
6. Key visual elements to emphasize for "{title}"

Keep it concise and actionable."""

            text = groq_chat(self.client, self.model, prompt, temperature=0.7, max_tokens=600)
            if text:
                return text
            return self._default_style_guide(product_data)

        except Exception as e:
            logger.error(f"Error generating style guide: {str(e)}")
            return self._default_style_guide(product_data)

    def _parse_json_array(self, text: str) -> List[str]:
        """Parse JSON array from response text"""
        try:
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception:
            pass
        return []

    def _default_image_prompts(self, product_data: Dict = None) -> List[str]:
        """Return product-aware default image prompts"""
        title = (product_data or {}).get("title", "Product")
        brand = (product_data or {}).get("brand", "")
        features = ", ".join((product_data or {}).get("features", [])[:3])
        brand_part = f"{brand} " if brand and brand != "Unknown Brand" else ""

        return [
            f"Professional {brand_part}{title} product photography, studio lighting, white background, sharp focus on product details, premium aesthetic. Features: {features}",
            f"Lifestyle shot of {title} on wooden desk, natural lighting, minimalist composition, inviting atmosphere, {features}",
            f"Close-up detail photography of {title}, dramatic lighting, shallow depth of field, highlighting texture and quality",
            f"{title} in lifestyle context, outdoor setting, golden hour lighting, soft shadows, inspiring composition",
            f"Flat lay photography of {title}, styled composition with complementary items, bright natural light, creative arrangement",
        ]

    def _default_video_scripts(self, product_data: Dict = None) -> List[str]:
        """Return product-aware default video scripts"""
        title = (product_data or {}).get("title", "this product")
        features = ", ".join((product_data or {}).get("features", [])[:2])

        return [
            f"[HOOK: {title} appears quickly] Hey, check out the {title}! [VISUAL: {features}] This changes everything. [VISUAL: Close-up of key feature] Don't sleep on this. [CTA: Link in bio]",
            f"[VISUAL: Problem scenario] Tired of the old way? [VISUAL: {title} solving problem] Meet the {title}. [VISUAL: Satisfaction moment] Trust us, you need this. [CTA: Shop now]",
        ]

    def _default_style_guide(self, product_data: Dict = None) -> str:
        title = (product_data or {}).get("title", "Product")
        return f"Modern, clean aesthetic for {title} with professional lighting and lifestyle context."

    def _default_prompts(self, product_data: Dict = None) -> Dict:
        """Return default prompts structure"""
        return {
            "image_prompts": self._default_image_prompts(product_data),
            "video_scripts": self._default_video_scripts(product_data),
            "visual_style_guide": self._default_style_guide(product_data),
        }


prompt_generation_agent = None
