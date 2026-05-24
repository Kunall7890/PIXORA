"""
Workflow Orchestration
Connects all agents for the complete creative generation pipeline
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Orchestrates the complete creative generation workflow"""

    def __init__(
        self,
        research_agent,
        enrichment_agent,
        strategy_agent,
        prompt_agent,
        critic_agent,
        image_generator,
        video_generator,
    ):
        self.research = research_agent
        self.enrichment = enrichment_agent
        self.strategy = strategy_agent
        self.prompt_gen = prompt_agent
        self.critic = critic_agent
        self.image_gen = image_generator
        self.video_gen = video_generator

    async def execute_workflow(
        self,
        url: str,
        brand_override: str = None,
        target_audience: str = None,
        custom_themes: Optional[List[str]] = None,
        max_retries: int = 2,
    ) -> Dict:
        """
        Execute complete creative generation workflow

        Steps:
        1. Product Research → Extract product data
        2. Creative Strategy → Generate creative brief
        3. Prompt Generation → Create optimized prompts
        4. Critic Review → Evaluate prompts
        5. Image Generation → Generate 5 images
        6. Video Generation → Generate 2 videos
        7. Final Assembly → Quality check
        """
        try:
            start_time = datetime.now()
            logger.info(f"🚀 Starting creative workflow for: {url}")

            # Step 1: Product Research
            logger.info("Step 1/7: Product Research Agent...")
            product_data = await self.research.extract_product_info(url)

            if not product_data.get("title") or product_data["title"] == "Product Unavailable":
                logger.error("Failed to extract product data")
                raise ValueError(f"Unable to access product URL: {url}")

            logger.info(f"✓ Extracted: {product_data['title']}")

            # Step 1b: LLM enrichment — product-only description & category
            logger.info("Step 1b/7: Product Enrichment (LLM)...")
            page_text = product_data.pop("page_text", "")
            product_data = self.enrichment.enrich(product_data, page_text=page_text)
            logger.info(f"✓ Description source: {product_data.get('extraction_source', 'scrape')}")

            # Step 2: Creative Strategy
            logger.info("Step 2/7: Creative Strategy Agent...")
            creative_brief = self.strategy.generate_strategy(
                product_data,
                brand_override=brand_override,
                target_audience=target_audience,
                custom_themes=custom_themes,
            )
            logger.info(f"✓ Strategy generated with {len(creative_brief.get('hooks', []))} hooks")

            # Step 3: Prompt Generation
            logger.info("Step 3/7: Prompt Generation Agent...")
            prompts = self.prompt_gen.generate_prompts(
                product_data, creative_brief, custom_themes=custom_themes
            )
            logger.info(
                f"✓ Generated {len(prompts['image_prompts'])} image prompts "
                f"& {len(prompts['video_scripts'])} video scripts"
            )

            # Step 4: Critic Review (Pre-Generation)
            logger.info("Step 4/7: Critic Review Agent (Pre-generation check)...")
            critic_review = self.critic.review_creatives(
                product_data,
                creative_brief,
                prompts["image_prompts"],
                prompts["video_scripts"],
            )
            logger.info(f"✓ Quality score: {critic_review['overall_quality']:.2f}")

            # Retry prompt generation if quality is low
            retries = 0
            while not critic_review["approved"] and retries < max_retries:
                logger.warning(
                    f"Quality below threshold — regenerating prompts (attempt {retries + 1})"
                )
                prompts = self.prompt_gen.generate_prompts(
                    product_data, creative_brief, custom_themes=custom_themes
                )
                critic_review = self.critic.review_creatives(
                    product_data,
                    creative_brief,
                    prompts["image_prompts"],
                    prompts["video_scripts"],
                )
                retries += 1

            # Step 5: Image Generation
            logger.info("Step 5/7: Image Generation Workflow...")
            images = await self.image_gen.generate_images(
                prompts["image_prompts"], product_data=product_data
            )
            logger.info(f"✓ Generated {len(images)} product images")

            # Step 6: Video Generation
            logger.info("Step 6/7: Video Generation Workflow...")
            videos = await self.video_gen.generate_videos(
                prompts["video_scripts"], product_data=product_data
            )
            logger.info(f"✓ Generated {len(videos)} product videos")

            # Step 7: Final Assembly
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            workflow_output = {
                "product_data": product_data,
                "creative_brief": creative_brief,
                "prompts": prompts,
                "images": images,
                "videos": videos,
                "critic_review": critic_review,
                "total_processing_time": processing_time,
                "status": "success",
                "pipeline_meta": {
                    "extraction_source": product_data.get("extraction_source", "unknown"),
                    "scrape_quality": product_data.get("scrape_quality", "unknown"),
                    "strategy_source": creative_brief.get("source", "unknown"),
                    "prompts_source": prompts.get("source", "unknown"),
                    "review_source": critic_review.get("source", "unknown"),
                    "engine_version": "2.2.0",
                },
            }

            logger.info(f"✓ Workflow completed in {processing_time:.1f} seconds")
            return workflow_output

        except Exception as e:
            logger.error(f"❌ Workflow failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "url": url,
            }

    async def execute_batch_workflow(
        self,
        items: List[Dict],
    ) -> Dict:
        """
        Execute workflow for multiple products

        Each item: {"url": str, "brand_override": str, "custom_themes": list}
        """
        job_id = str(uuid.uuid4())[:8]
        logger.info(f"📦 Starting batch processing job: {job_id}")

        results = []
        failed = []

        for i, item in enumerate(items, 1):
            url = item.get("url")
            logger.info(f"Processing {i}/{len(items)}: {url}")
            try:
                result = await self.execute_workflow(
                    url=url,
                    brand_override=item.get("brand_override"),
                    target_audience=item.get("target_audience"),
                    custom_themes=item.get("custom_themes"),
                )
                if result.get("status") == "failed":
                    failed.append({"url": url, "error": result.get("error")})
                else:
                    results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {url}: {str(e)}")
                failed.append({"url": url, "error": str(e)})

        return {
            "job_id": job_id,
            "status": "completed",
            "total_urls": len(items),
            "processed": len(results),
            "failed": len(failed),
            "results": results,
            "failed_urls": failed,
        }


workflow_orchestrator = None
