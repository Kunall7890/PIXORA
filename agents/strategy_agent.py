"""
Creative Strategy Agent
Generates creative directions for marketing campaigns
"""
import logging
from typing import Dict, List
from groq import Groq

logger = logging.getLogger(__name__)


class CreativeStrategyAgent:
    """Generates creative strategy and marketing angles from product data"""
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "mixtral-8x7b-32768"
    
    def generate_strategy(self, product_data: Dict, brand_override: str = None) -> Dict:
        """
        Generate creative strategy from product information
        
        Returns:
            Dict with hooks, target_audience, visual_themes, color_palette, 
            marketing_angles, ad_captions, tone_of_voice
        """
        try:
            logger.info(f"Generating creative strategy for: {product_data.get('title')}")
            
            brand = brand_override or product_data.get("brand", "the brand")
            
            prompt = self._build_strategy_prompt(product_data, brand)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            
            # Parse response and structure it
            strategy = self._parse_strategy_response(response.choices[0].message.content)
            logger.info("✓ Creative strategy generated successfully")
            return strategy
            
        except Exception as e:
            logger.error(f"Error generating strategy: {str(e)}")
            return self._default_strategy()
    
    def _build_strategy_prompt(self, product_data: Dict, brand: str) -> str:
        """Build prompt for creative strategy generation"""
        
        title = product_data.get("title", "Product")
        description = product_data.get("description", "")
        features = ", ".join(product_data.get("features", [])[:5])
        price = product_data.get("price")
        rating = product_data.get("rating")
        
        prompt = f"""You are an expert marketing strategist for e-commerce brands. 
Generate a creative marketing strategy for this product.

PRODUCT INFO:
- Brand: {brand}
- Title: {title}
- Description: {description}
- Key Features: {features}
- Price: ${price if price else 'N/A'}
- Rating: {f"{rating}/5" if rating else 'Not rated'}

Generate EXACTLY this JSON structure (no markdown, pure JSON):
{{
    "hooks": ["hook1", "hook2", "hook3", "hook4", "hook5"],
    "target_audience": "specific demographic description",
    "visual_themes": ["theme1", "theme2", "theme3"],
    "color_palette": ["color1", "color2", "color3", "color4"],
    "marketing_angles": ["angle1", "angle2", "angle3"],
    "ad_captions": ["caption1", "caption2", "caption3"],
    "tone_of_voice": "tone description"
}}

Hooks should be compelling, attention-grabbing openings for short videos.
Target audience should be specific (age, interests, lifestyle).
Visual themes should describe the aesthetic style.
Color palette should be hex codes or color names.
Marketing angles should be unique value propositions.
Captions should be witty, engaging, product-focused.
Tone should match the product's brand personality."""
        
        return prompt
    
    def _parse_strategy_response(self, response_text: str) -> Dict:
        """Parse LLM response into structured strategy"""
        import json
        import re
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                strategy = json.loads(json_str)
                return {
                    "hooks": strategy.get("hooks", []),
                    "target_audience": strategy.get("target_audience", "General audience"),
                    "visual_themes": strategy.get("visual_themes", []),
                    "color_palette": strategy.get("color_palette", []),
                    "marketing_angles": strategy.get("marketing_angles", []),
                    "ad_captions": strategy.get("ad_captions", []),
                    "tone_of_voice": strategy.get("tone_of_voice", "Professional and engaging"),
                }
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, returning default")
        
        return self._default_strategy()
    
    def _default_strategy(self) -> Dict:
        """Return default strategy when generation fails"""
        return {
            "hooks": [
                "Introducing the ultimate solution",
                "Transform your daily routine",
                "Experience the difference",
                "Quality meets affordability",
                "Discover what you've been missing"
            ],
            "target_audience": "Young professionals seeking quality products",
            "visual_themes": ["Modern minimalist", "Lifestyle action shots", "Product close-ups"],
            "color_palette": ["#000000", "#FFFFFF", "#FF6B6B", "#4ECDC4"],
            "marketing_angles": [
                "Superior quality at competitive price",
                "Life-changing features",
                "Trusted by thousands"
            ],
            "ad_captions": [
                "Your new favorite product",
                "Don't miss out",
                "Limited availability"
            ],
            "tone_of_voice": "Professional, enthusiastic, and customer-focused"
        }


# Instantiate agent
creative_strategy_agent = None  # Will be initialized in main.py with API key