"""
Product Enrichment Agent
Uses LLM to produce a clean, product-only description and structured facts
from scraped page data (fixes website-level meta descriptions).
"""
import logging
from typing import Dict, List, Optional

from groq import Groq

import config
from agents.groq_utils import groq_chat, parse_json_object

logger = logging.getLogger(__name__)

ENRICHMENT_SYSTEM = """You are an e-commerce product data specialist.
You receive scraped data from a product page. Your job is to extract ONLY information
about the specific product being sold — NOT the website, store, or company tagline.

Rules:
- Description must explain what the product IS and what it DOES for the buyer
- Never copy generic site slogans like "Free shipping", "Best online store", "Shop now"
- Use only facts present in the input; do not invent specs or features
- If data is thin, write a short honest description based on title and visible facts
- Output valid JSON only, no markdown"""


class ProductEnrichmentAgent:
    """Refines scraped product data into accurate product-specific records."""

    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key) if groq_api_key else None
        self.model = config.GROQ_MODEL

    def enrich(self, product_data: Dict, page_text: str = "") -> Dict:
        """
        Return enriched product_data with product-only description and cleaned fields.
        Mutates and returns the same dict for pipeline convenience.
        """
        if not self.client:
            logger.warning("No Groq client — skipping product enrichment")
            return self._fallback_from_title(product_data)

        title = product_data.get("title", "")
        if not title or title in ("Unknown Product", "Product Unavailable"):
            return product_data

        title = product_data.get("title", "")
        url = product_data.get("url", "")
        scrape_quality = product_data.get("scrape_quality", "low")

        prompt = self._build_prompt(product_data, page_text, scrape_quality)
        text = groq_chat(
            self.client,
            self.model,
            prompt,
            temperature=0.2,
            max_tokens=1200,
            system=ENRICHMENT_SYSTEM,
        )

        parsed = parse_json_object(text)
        if not parsed:
            logger.warning(f"Enrichment JSON parse failed for: {title}")
            product_data = self._fallback_from_title(product_data)
            return product_data

        if parsed.get("product_description"):
            product_data["description"] = parsed["product_description"].strip()
        if parsed.get("short_summary"):
            product_data["short_summary"] = parsed["short_summary"].strip()
        if parsed.get("category"):
            product_data["category"] = parsed["category"].strip()
        if parsed.get("key_features") and isinstance(parsed["key_features"], list):
            clean = [f for f in parsed["key_features"] if f and len(f) > 3]
            if clean:
                product_data["features"] = clean[:12]
        if parsed.get("brand") and parsed["brand"] != "Unknown":
            product_data["brand"] = parsed["brand"]

        product_data["extraction_source"] = "enriched"
        logger.info(f"✓ Enriched product description for: {title}")
        return product_data

    def _fallback_from_title(self, product_data: Dict) -> Dict:
        """Minimal enrichment when LLM parse fails but we have a title."""
        title = product_data.get("title", "")
        if title and not product_data.get("description"):
            product_data["description"] = (
                f"{title} — premium product available for online purchase."
            )
        product_data["extraction_source"] = "title_fallback"
        return product_data

    def _build_prompt(self, product_data: Dict, page_text: str, scrape_quality: str = "low") -> str:
        title = product_data.get("title", "")
        raw_desc = product_data.get("description", "")
        features = product_data.get("features", [])
        specs = product_data.get("specs", {})
        brand = product_data.get("brand", "")
        price = product_data.get("price")
        currency = product_data.get("currency", "USD")
        rating = product_data.get("rating")
        url = product_data.get("url", "")

        page_snippet = (page_text or "")[:3500]

        quality_note = ""
        if scrape_quality == "low":
            quality_note = """
IMPORTANT: Scraped data is incomplete (page may have been partially blocked).
Use the product TITLE and URL to infer accurate product category and realistic key features.
For smartphones: mention storage, camera, display, battery, processor if inferable from title.
For headphones: mention bluetooth, battery life, driver size, noise cancellation if applicable.
For shoes/clothing: mention material, fit, size, color from title.
Do NOT invent exact specs not implied by the title — use general accurate category features."""

        return f"""Analyze this product and return product-only facts.
{quality_note}

PRODUCT PAGE URL: {url}
PRODUCT TITLE: {title}
SCRAPED BRAND: {brand}
SCRAPED PRICE: {currency} {price if price else 'unknown'}
SCRAPED RATING: {rating if rating else 'unknown'}
SCRAPED DESCRIPTION:
{raw_desc or 'not available'}

SCRAPED FEATURES:
{chr(10).join(f'- {f}' for f in features[:12]) or 'none'}

SCRAPED SPECS:
{chr(10).join(f'- {k}: {v}' for k, v in list(specs.items())[:8]) or 'none'}

PAGE TEXT:
{page_snippet or 'not available'}

Return JSON:
{{
  "product_description": "2-4 sentences about THIS specific product — what it is, who it's for, key benefits",
  "short_summary": "one line pitch for {title}",
  "category": "product category",
  "key_features": ["6-10 key features of {title} — real specs from data or reasonable from title/category"],
  "brand": "brand name"
}}"""
