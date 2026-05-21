"""
Prompt Generation Agent
Creates optimized prompts for image and video generation models
"""
import logging
from typing import Dict, List
from groq import Groq
import json
import re

logger = logging.getLogger(__name__)


class PromptGenerationAgent:
    """Generates optimized prompts for SDXL and video models"""
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "mixtral-8x7b-32768"
    
    def generate_prompts(self, product_data: Dict, creative_brief: Dict) -> Dict:
        """
        Generate optimized image and video prompts
        
        Returns:
            Dict with image_prompts, video_scripts, visual_style_guide
        """
        try:
            logger.info("Generating optimized prompts for generation models")
            
            # Generate image prompts
            image_prompts = self._generate_image_prompts(product_data, creative_brief)
            
            # Generate video scripts
            video_scripts = self._generate_video_scripts(product_data, creative_brief)
            
            # Generate style guide
            style_guide = self._generate_style_guide(product_data, creative_brief)
            
            logger.info("✓ Prompts generated successfully")
            return {
                "image_prompts": image_prompts,
                "video_scripts": video_scripts,
                "visual_style_guide": style_guide
            }
            
        except Exception as e:
            logger.error(f"Error generating prompts: {str(e)}")
            return self._default_prompts()
    
    def _generate_image_prompts(self, product_data: Dict, creative_brief: Dict) -> List[str]:
        """Generate 5 varied image prompts for SDXL"""
        try:
            title = product_data.get("title", "Product")
            features = ", ".join(product_data.get("features", [])[:3])
            themes = creative_brief.get("visual_themes", [])
            colors = creative_brief.get("color_palette", [])
            
            prompt = f"""You are an expert prompt engineer for Stable Diffusion XL. 
Generate 5 DIFFERENT high-quality image prompts for marketing photography.

PRODUCT: {title}
FEATURES: {features}
VISUAL THEMES: {', '.join(themes)}
COLOR PALETTE: {', '.join(colors)}

Create 5 UNIQUE prompts for product photography. Each prompt should:
- Be detailed and specific (50-100 words each)
- Include lighting, composition, and mood
- Avoid hands/people unless essential
- Focus on product showcase with lifestyle context
- Include photography style (e.g., "studio shot", "lifestyle photography")
- Specify color grading and atmosphere

Return as JSON array of 5 strings, nothing else:
["prompt1", "prompt2", "prompt3", "prompt4", "prompt5"]"""
            
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1500,
            )
            
            prompts = self._parse_json_array(response.content[0].text)
            if len(prompts) < 5:
                prompts.extend(self._default_image_prompts()[:5-len(prompts)])
            
            return prompts[:5]
        
        except Exception as e:
            logger.error(f"Error generating image prompts: {str(e)}")
            return self._default_image_prompts()
    
    def _generate_video_scripts(self, product_data: Dict, creative_brief: Dict) -> List[str]:
        """Generate 2 video scripts for short-form video generation"""
        try:
            title = product_data.get("title", "Product")
            description = product_data.get("description", "")
            hooks = creative_brief.get("hooks", [])
            captions = creative_brief.get("ad_captions", [])
            
            prompt = f"""You are an expert video copywriter for short-form content (TikTok, Reels, Shorts).
Generate 2 DIFFERENT video scripts for 8-15 second product marketing videos.

PRODUCT: {title}
DESCRIPTION: {description}
HOOKS: {', '.join(hooks[:2])}
CAPTIONS: {', '.join(captions[:2])}

Each script should:
- Be 8-15 seconds when read at normal pace
- Start with an attention-grabbing hook
- Include product showcase moment
- End with call-to-action
- Be engaging and conversational
- Include [VISUAL: ...] descriptions for key moments

Return as JSON array of 2 strings:
["script1", "script2"]"""
            
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1500,
            )
            
            scripts = self._parse_json_array(response.content[0].text)
            if len(scripts) < 2:
                scripts.extend(self._default_video_scripts()[:2-len(scripts)])
            
            return scripts[:2]
        
        except Exception as e:
            logger.error(f"Error generating video scripts: {str(e)}")
            return self._default_video_scripts()
    
    def _generate_style_guide(self, product_data: Dict, creative_brief: Dict) -> str:
        """Generate visual style guide for consistency"""
        try:
            themes = creative_brief.get("visual_themes", [])
            colors = creative_brief.get("color_palette", [])
            tone = creative_brief.get("tone_of_voice", "")
            
            prompt = f"""You are a creative director. Generate a concise visual style guide.

VISUAL THEMES: {', '.join(themes)}
COLOR PALETTE: {', '.join(colors)}
TONE: {tone}

Create a style guide covering:
1. Overall aesthetic (1-2 sentences)
2. Photography style and mood
3. Color usage guidelines
4. Typography hints (if applicable)
5. Composition principles
6. Lighting approach
7. Key visual elements to emphasize

Keep it concise and actionable."""
            
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Error generating style guide: {str(e)}")
            return "Modern, clean aesthetic with professional lighting and lifestyle context."
    
    def _parse_json_array(self, text: str) -> List[str]:
        """Parse JSON array from response text"""
        try:
            # Find JSON array in text
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except:
            pass
        return []
    
    def _default_image_prompts(self) -> List[str]:
        """Return default image prompts"""
        return [
            "Professional product photography, studio lighting, white background, sharp focus on product details, premium aesthetic",
            "Lifestyle product shot on wooden desk, natural lighting, book and coffee nearby, minimalist composition, inviting atmosphere",
            "Close-up product detail photography, dramatic lighting, shallow depth of field, highlighting texture and quality",
            "Product in lifestyle context, outdoor setting, golden hour lighting, soft shadows, inspiring composition",
            "Flat lay product photography, styled composition with complementary items, bright natural light, creative arrangement"
        ]
    
    def _default_video_scripts(self) -> List[str]:
        """Return default video scripts"""
        return [
            "[HOOK: Product appears quickly] Hey, check THIS out! [VISUAL: Product benefits showcase] This changes everything. [VISUAL: Close-up of key feature] Don't sleep on this. [CTA: Link in bio]",
            "[VISUAL: Problem scenario] Tired of the old way? [VISUAL: Product solving problem] Meet your new favorite. [VISUAL: Satisfaction moment] Trust us, you need this. [CTA: Shop now]"
        ]
    
    def _default_prompts(self) -> Dict:
        """Return default prompts structure"""
        return {
            "image_prompts": self._default_image_prompts(),
            "video_scripts": self._default_video_scripts(),
            "visual_style_guide": "Modern, professional aesthetic with clean composition and engaging lifestyle context."
        }


# Instantiate agent
prompt_generation_agent = None  # Will be initialized in main.py with API key
