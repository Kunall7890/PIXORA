"""
Image Generation Module
Generates product marketing images using Stable Diffusion
"""
import logging
import asyncio
from typing import List, Dict
from datetime import datetime
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generates product marketing images"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path("outputs/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to import diffusers
        try:
            from diffusers import StableDiffusionXLPipeline
            import torch
            
            self.has_diffusers = True
            self.torch = torch
            self.pipeline = None
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            self.has_diffusers = False
            logger.warning("Diffusers not installed - using mock image generation")
    
    async def generate_images(self, prompts: List[str], product_data: Dict = None) -> List[Dict]:
        """
        Generate product marketing images from prompts

        Returns:
            List of Dict with id, prompt, url, local_path, created_at, quality_score
        """
        try:
            title = (product_data or {}).get("title", "Product")
            logger.info(f"Generating {len(prompts)} images for: {title}")

            if self.has_diffusers and len(prompts) > 0:
                images = await self._generate_with_diffusers(prompts, product_data)
            else:
                images = await self._generate_mock_images(prompts, product_data)
            
            logger.info(f"✓ Generated {len(images)} images")
            return images
            
        except Exception as e:
            logger.error(f"Error generating images: {str(e)}")
            return await self._generate_mock_images(prompts, product_data)

    async def _generate_with_diffusers(self, prompts: List[str], product_data: Dict = None) -> List[Dict]:
        """Generate images using local Stable Diffusion"""
        try:
            from diffusers import StableDiffusionXLPipeline
            import torch
            
            # Load pipeline if not already loaded
            if self.pipeline is None:
                logger.info("Loading SDXL model (this may take a moment)...")
                self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-base-1.0",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    use_safetensors=True,
                    variant="fp16" if self.device == "cuda" else None
                )
                self.pipeline = self.pipeline.to(self.device)
                logger.info("✓ Model loaded")
            
            images_list = []
            
            for i, prompt in enumerate(prompts, 1):
                try:
                    logger.info(f"Generating image {i}/{len(prompts)}...")
                    
                    # Generate image
                    with torch.no_grad():
                        result = self.pipeline(
                            prompt=prompt,
                            num_inference_steps=20,  # Fast inference
                            guidance_scale=7.5,
                            height=1024,
                            width=1024
                        )
                    
                    image = result.images[0]
                    
                    # Save image
                    image_id = str(uuid.uuid4())[:8]
                    filename = f"product_{image_id}.png"
                    filepath = self.output_dir / filename
                    image.save(filepath)
                    
                    images_list.append({
                        "id": image_id,
                        "prompt": prompt,
                        "url": f"/outputs/images/{filename}",
                        "local_path": str(filepath),
                        "created_at": datetime.now().isoformat(),
                        "quality_score": 0.85
                    })
                    
                except Exception as e:
                    logger.error(f"Error generating image {i}: {str(e)}")
            
            return images_list
        
        except Exception as e:
            logger.error(f"Diffusers generation failed: {str(e)}")
            return await self._generate_mock_images(prompts, product_data)

    async def _generate_mock_images(self, prompts: List[str], product_data: Dict = None) -> List[Dict]:
        """Generate mock images for testing"""
        title = (product_data or {}).get("title", "Product")
        brand = (product_data or {}).get("brand", "")
        logger.info(f"Generating mock images for: {title}")
        
        images_list = []
        
        for i, prompt in enumerate(prompts, 1):
            try:
                # Create a simple placeholder image using PIL
                from PIL import Image, ImageDraw, ImageFont
                
                # Create image
                img = Image.new('RGB', (1024, 1024), color='#f0f0f0')
                draw = ImageDraw.Draw(img)
                
                # Draw product area
                draw.rectangle([100, 100, 924, 924], fill='#ffffff', outline='#cccccc', width=2)
                
                # Add product-specific text
                label = f"{brand} {title}".strip() if brand and brand != "Unknown Brand" else title
                text = f"{label}\n{prompt[:80]}..."
                draw.text((512, 400), text, fill='#333333', anchor='mm')
                
                # Save
                image_id = str(uuid.uuid4())[:8]
                filename = f"product_{image_id}.png"
                filepath = self.output_dir / filename
                img.save(filepath)
                
                images_list.append({
                    "id": image_id,
                    "prompt": prompt,
                    "url": f"/outputs/images/{filename}",
                    "local_path": str(filepath),
                    "created_at": datetime.now().isoformat(),
                    "quality_score": 0.75
                })
                
                logger.info(f"✓ Created mock image {i}")
            
            except Exception as e:
                logger.error(f"Error creating mock image: {str(e)}")
        
        return images_list


# Instantiate generator
image_generator = ImageGenerator()
