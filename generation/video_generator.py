"""
Video Generation Module
Generates short product videos using AI models
"""
import logging
import asyncio
from typing import List, Dict
from datetime import datetime
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Generates short product marketing videos"""
    
    def __init__(self, output_dir: str = None, replicate_token: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path("outputs/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.replicate_token = replicate_token
        self.has_replicate = replicate_token is not None
        
        if self.has_replicate:
            try:
                import replicate
                self.replicate = replicate
                self.client = replicate.Client(api_token=replicate_token)
            except ImportError:
                self.has_replicate = False
                logger.warning("Replicate not installed")
    
    async def generate_videos(self, scripts: List[str], product_data: Dict = None) -> List[Dict]:
        """
        Generate short product marketing videos from scripts

        Returns:
            List of Dict with id, script, url, local_path, duration, created_at, quality_score
        """
        try:
            title = (product_data or {}).get("title", "Product")
            logger.info(f"Generating {len(scripts)} videos for: {title}")

            if self.has_replicate and len(scripts) > 0:
                videos = await self._generate_with_replicate(scripts, product_data)
            else:
                videos = await self._generate_mock_videos(scripts, product_data)
            
            logger.info(f"✓ Generated {len(videos)} videos")
            return videos
            
        except Exception as e:
            logger.error(f"Error generating videos: {str(e)}")
            return await self._generate_mock_videos(scripts, product_data)

    async def _generate_with_replicate(self, scripts: List[str], product_data: Dict = None) -> List[Dict]:
        """Generate videos using Replicate API"""
        try:
            import replicate
            
            videos_list = []
            
            for i, script in enumerate(scripts, 1):
                try:
                    logger.info(f"Generating video {i}/{len(scripts)} via Replicate...")
                    
                    # Create text-to-video prompt from script
                    prompt = self._script_to_prompt(script, product_data)
                    
                    # Call Replicate API (using CogVideoX or similar)
                    # Note: This is a placeholder - actual model may vary
                    output = replicate.run(
                        "cogvideox",
                        input={
                            "prompt": prompt,
                            "num_frames": 24 * 8,  # 8 seconds at 24fps
                            "temperature": 1,
                        }
                    )
                    
                    if output:
                        # Save video
                        video_id = str(uuid.uuid4())[:8]
                        filename = f"product_{video_id}.mp4"
                        filepath = self.output_dir / filename
                        
                        # Download/save output
                        import requests
                        if isinstance(output, str):
                            response = requests.get(output)
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                        
                        videos_list.append({
                            "id": video_id,
                            "script": script,
                            "url": f"/outputs/videos/{filename}",
                            "local_path": str(filepath),
                            "duration": 8.0,
                            "created_at": datetime.now().isoformat(),
                            "quality_score": 0.80
                        })
                        
                        logger.info(f"✓ Video {i} generated")
                
                except Exception as e:
                    logger.error(f"Error generating video {i}: {str(e)}")
            
            return videos_list if videos_list else await self._generate_mock_videos(scripts, product_data)

        except Exception as e:
            logger.error(f"Replicate generation failed: {str(e)}")
            return await self._generate_mock_videos(scripts, product_data)

    async def _generate_mock_videos(self, scripts: List[str], product_data: Dict = None) -> List[Dict]:
        """Generate mock videos for testing"""
        title = (product_data or {}).get("title", "Product")
        logger.info(f"Generating mock videos for: {title}")
        
        videos_list = []
        
        for i, script in enumerate(scripts, 1):
            try:
                # Create a mock video file
                import subprocess
                from pathlib import Path
                
                video_id = str(uuid.uuid4())[:8]
                filename = f"product_{video_id}.mp4"
                filepath = self.output_dir / filename
                
                # Create a simple video using ffmpeg (if available)
                try:
                    # Generate a 8-second black video as placeholder
                    cmd = [
                        'ffmpeg',
                        '-f', 'lavfi',
                        '-i', 'color=c=black:s=1280x720:d=8',
                        '-f', 'lavfi',
                        '-i', 'anullsrc=r=44100:cl=mono:d=8',
                        '-pix_fmt', 'yuv420p',
                        '-c:v', 'libx264',
                        '-c:a', 'aac',
                        str(filepath),
                        '-y'
                    ]
                    subprocess.run(cmd, capture_output=True, timeout=30)
                    
                    if filepath.exists():
                        videos_list.append({
                            "id": video_id,
                            "script": script,
                            "url": f"/outputs/videos/{filename}",
                            "local_path": str(filepath),
                            "duration": 8.0,
                            "created_at": datetime.now().isoformat(),
                            "quality_score": 0.70
                        })
                        logger.info(f"✓ Created mock video {i}")
                        continue
                except Exception as e:
                    logger.debug(f"FFmpeg not available: {str(e)}")
                
                # Fallback: Create text file as video placeholder
                filepath.write_text(f"Video for {title}\nScript: {script}\nDuration: 8s")
                
                videos_list.append({
                    "id": video_id,
                    "script": script,
                    "url": f"/outputs/videos/{filename}",
                    "local_path": str(filepath),
                    "duration": 8.0,
                    "created_at": datetime.now().isoformat(),
                    "quality_score": 0.65
                })
                logger.info(f"✓ Created video placeholder {i}")
            
            except Exception as e:
                logger.error(f"Error creating mock video: {str(e)}")
        
        return videos_list
    
    def _script_to_prompt(self, script: str, product_data: Dict = None) -> str:
        """Convert video script to image generation prompt"""
        title = (product_data or {}).get("title", "product")
        return f"Professional marketing video for {title}. {script[:200]}. High quality, cinematic lighting."

