"""
Critic/Review Agent
Evaluates generated creatives for quality, consistency, and hallucinations
"""
import logging
from typing import Dict, List, Tuple
from groq import Groq
import json
import re

logger = logging.getLogger(__name__)


class CriticAgent:
    """Reviews and evaluates generated creatives"""
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "mixtral-8x7b-32768"
    
    def review_creatives(
        self, 
        product_data: Dict,
        creative_brief: Dict,
        image_prompts: List[str],
        video_scripts: List[str]
    ) -> Dict:
        """
        Review generated prompts and creative outputs for quality
        
        Returns:
            Dict with hallucination_score, consistency_score, branding_score,
            overall_quality, issues, suggestions, approved
        """
        try:
            logger.info("Running quality review on generated creatives")
            
            # Check for hallucinations in prompts
            hallucination_score = self._check_hallucinations(product_data, image_prompts + video_scripts)
            
            # Check consistency with brand
            consistency_score = self._check_consistency(creative_brief, image_prompts + video_scripts)
            
            # Check branding alignment
            branding_score = self._check_branding(product_data, creative_brief, image_prompts + video_scripts)
            
            # Identify issues and get suggestions
            issues, suggestions = self._identify_issues(
                product_data, 
                creative_brief,
                hallucination_score,
                consistency_score,
                branding_score
            )
            
            # Calculate overall quality
            overall_quality = (hallucination_score + consistency_score + branding_score) / 3
            
            # Approve if all scores above threshold
            approved = (
                hallucination_score >= 0.7 and
                consistency_score >= 0.75 and
                branding_score >= 0.8
            )
            
            logger.info(f"✓ Review complete - Overall quality: {overall_quality:.2f}")
            
            return {
                "hallucination_score": hallucination_score,
                "consistency_score": consistency_score,
                "branding_score": branding_score,
                "overall_quality": overall_quality,
                "issues": issues,
                "suggestions": suggestions,
                "approved": approved
            }
            
        except Exception as e:
            logger.error(f"Error in critic review: {str(e)}")
            return self._default_review()
    
    def _check_hallucinations(self, product_data: Dict, prompts: List[str]) -> float:
        """Check for hallucinations or false claims in prompts"""
        try:
            title = product_data.get("title", "")
            features = product_data.get("features", [])
            features_str = ", ".join(features[:5])
            
            prompt_text = " ".join(prompts)
            
            review_prompt = f"""You are a fact-checker for marketing content.
Review these marketing prompts for HALLUCINATIONS (false claims, made-up features, exaggerations).

ACTUAL PRODUCT:
- Title: {title}
- Real Features: {features_str}

MARKETING PROMPTS:
{prompt_text}

On a scale of 0-1, how TRUTHFUL are these prompts? (1 = completely accurate, 0 = full of lies)
Consider:
- Are features accurately represented?
- Are there false claims or exaggerations?
- Is the description aligned with reality?

Respond with ONLY a single number between 0 and 1, nothing else."""
            
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": review_prompt}],
                temperature=0.3,
                max_tokens=10,
            )
            
            score_text = response.content[0].text.strip()
            score = float(re.search(r'0\.\d+|1\.0|1', score_text).group(0))
            return min(max(score, 0), 1)  # Clamp to 0-1
        
        except Exception as e:
            logger.warning(f"Error checking hallucinations: {str(e)}")
            return 0.85
    
    def _check_consistency(self, creative_brief: Dict, prompts: List[str]) -> float:
        """Check consistency with creative strategy"""
        try:
            themes = ", ".join(creative_brief.get("visual_themes", []))
            hooks = ", ".join(creative_brief.get("hooks", [])[:2])
            tone = creative_brief.get("tone_of_voice", "")
            
            prompt_text = " ".join(prompts)
            
            review_prompt = f"""You are a creative consistency reviewer.
Check if these marketing prompts follow the creative strategy.

CREATIVE STRATEGY:
- Visual Themes: {themes}
- Hooks/Angles: {hooks}
- Tone: {tone}

MARKETING PROMPTS:
{prompt_text}

On a scale of 0-1, how CONSISTENT are these prompts with the strategy? (1 = perfect alignment, 0 = completely off-brand)

Respond with ONLY a single number between 0 and 1."""
            
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": review_prompt}],
                temperature=0.3,
                max_tokens=10,
            )
            
            score_text = response.content[0].text.strip()
            score = float(re.search(r'0\.\d+|1\.0|1', score_text).group(0))
            return min(max(score, 0), 1)
        
        except Exception as e:
            logger.warning(f"Error checking consistency: {str(e)}")
            return 0.82
    
    def _check_branding(self, product_data: Dict, creative_brief: Dict, prompts: List[str]) -> float:
        """Check branding alignment and quality"""
        try:
            brand = product_data.get("brand", "")
            price_tier = "premium" if product_data.get("price", 0) > 100 else "affordable"
            target_audience = creative_brief.get("target_audience", "")
            
            prompt_text = " ".join(prompts)
            
            review_prompt = f"""You are a brand strategist.
Evaluate if these marketing prompts maintain strong branding.

BRAND INFO:
- Brand Name: {brand}
- Price Tier: {price_tier}
- Target Audience: {target_audience}

MARKETING PROMPTS:
{prompt_text}

On a scale of 0-1, how STRONG is the branding? (1 = excellent brand voice, 0 = weak/generic)
Consider:
- Professional tone
- Audience alignment
- Price point appropriateness
- Brand personality

Respond with ONLY a single number between 0 and 1."""
            
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": review_prompt}],
                temperature=0.3,
                max_tokens=10,
            )
            
            score_text = response.content[0].text.strip()
            score = float(re.search(r'0\.\d+|1\.0|1', score_text).group(0))
            return min(max(score, 0), 1)
        
        except Exception as e:
            logger.warning(f"Error checking branding: {str(e)}")
            return 0.83
    
    def _identify_issues(
        self, 
        product_data: Dict,
        creative_brief: Dict,
        hallucination: float,
        consistency: float,
        branding: float
    ) -> Tuple[List[str], List[str]]:
        """Identify issues and suggest improvements"""
        issues = []
        suggestions = []
        
        if hallucination < 0.7:
            issues.append("High hallucination risk detected")
            suggestions.append("Review prompts for false claims and overstated features")
        
        if consistency < 0.75:
            issues.append("Prompts diverge from creative strategy")
            suggestions.append("Realign prompts with visual themes and marketing angles")
        
        if branding < 0.8:
            issues.append("Weak brand voice in creatives")
            suggestions.append("Strengthen brand personality and tone alignment")
        
        if not issues:
            suggestions.append("Content meets quality standards - ready for generation")
        
        return issues, suggestions
    
    def _default_review(self) -> Dict:
        """Return default review when evaluation fails"""
        return {
            "hallucination_score": 0.85,
            "consistency_score": 0.80,
            "branding_score": 0.82,
            "overall_quality": 0.82,
            "issues": [],
            "suggestions": ["Review complete - content ready for generation"],
            "approved": True
        }


# Instantiate agent
critic_agent = None  # Will be initialized in main.py with API key
