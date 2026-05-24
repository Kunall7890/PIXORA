"""Flipkart product data extractor from embedded __INITIAL_STATE__ JSON."""
import logging
import re
from typing import Dict, List, Optional

from agents.extractors.common import (
    deep_extract_highlights,
    merge_feature_lists,
    parse_description_features,
    specs_dict_to_features,
)
from agents.extractors.json_utils import extract_balanced_json

logger = logging.getLogger(__name__)


def extract_flipkart_product(html: str) -> Optional[Dict]:
    """Parse Flipkart window.__INITIAL_STATE__ for product facts."""
    try:
        state = extract_balanced_json(html, "window.__INITIAL_STATE__")
        if not state:
            return None

        page_resp = state.get("multiWidgetState", {}).get("pageDataResponse", {})
        if not page_resp:
            return None

        result: Dict = {}

        # SEO block — reliable for ALL Flipkart categories
        seo_data = page_resp.get("seoData", {})
        seo = seo_data.get("seo", {})
        if seo.get("title"):
            result["title"] = seo["title"]
        if seo.get("description"):
            result["description"] = seo["description"]

        # Schema.org product
        for schema in seo_data.get("schema") or []:
            if not isinstance(schema, dict):
                continue
            _merge_schema(result, schema)

        # Price from tracking context
        try:
            ppd = (
                page_resp.get("pageContext", {})
                .get("fdpEventTracking", {})
                .get("events", {})
                .get("psi", {})
                .get("ppd", {})
            )
            if isinstance(ppd, dict):
                if not result.get("price") and ppd.get("finalPrice"):
                    result["price"] = float(ppd["finalPrice"])
                if ppd.get("mrp"):
                    result["mrp"] = float(ppd["mrp"])
        except Exception:
            pass

        title = result.get("title", "")

        # Deep walk entire state for highlights/specs (works for phones, fashion, home, etc.)
        tree_highlights = deep_extract_highlights(state, title)

        # Widget regex fallback
        widget_highlights = _regex_widget_highlights(
            state.get("multiWidgetState", {}).get("widgetsData", {}),
            title,
        )

        # Spec tables in widgets
        specs = _extract_spec_tables(state)
        if specs:
            result["specs"] = specs

        desc_features = parse_description_features(result.get("description", ""), title)

        result["features"] = merge_feature_lists(
            desc_features,
            specs_dict_to_features(specs or {}),
            tree_highlights,
            widget_highlights,
            title=title,
        )

        if result.get("title") or result.get("description"):
            logger.info(f"Flipkart extracted: {result.get('title', '')[:60]}")
            return result

        return None

    except Exception as e:
        logger.warning(f"Flipkart state parse failed: {e}")
        return None


def _merge_schema(result: Dict, schema: dict) -> None:
    stype = schema.get("@type", "")
    if stype not in ("Product", "IndividualProduct") and not schema.get("name"):
        return

    if schema.get("name") and not result.get("title"):
        result["title"] = schema["name"]
    if schema.get("description") and not result.get("description"):
        result["description"] = schema["description"]

    brand = schema.get("brand")
    if isinstance(brand, dict) and brand.get("name"):
        result["brand"] = brand["name"].title()
    elif isinstance(brand, str):
        result["brand"] = brand.title()

    rating_block = schema.get("aggregateRating", {})
    if isinstance(rating_block, dict):
        if rating_block.get("ratingValue"):
            try:
                result["rating"] = float(rating_block["ratingValue"])
            except (ValueError, TypeError):
                pass
        rc = rating_block.get("reviewCount") or rating_block.get("ratingCount")
        if rc:
            result["reviews"] = f"{rc} ratings & reviews"

    offers = schema.get("offers", {})
    if isinstance(offers, dict):
        price = offers.get("price") or offers.get("lowPrice")
        if price:
            try:
                result["price"] = float(str(price).replace(",", ""))
            except (ValueError, TypeError):
                pass
        result["currency"] = offers.get("priceCurrency", "INR")

    images = schema.get("image")
    if isinstance(images, str):
        result["image_urls"] = [images]
    elif isinstance(images, list):
        result["image_urls"] = [i for i in images if isinstance(i, str)]


def _regex_widget_highlights(widgets_data: dict, title: str) -> List[str]:
    """Regex fallback for highlight strings in widget JSON blob."""
    import json
    from agents.product_sanitizer import is_junk_feature

    highlights = []
    blob = json.dumps(widgets_data, ensure_ascii=False)

    for match in re.finditer(r'"(?:text|value|title)"\s*:\s*"([^"]{8,220})"', blob):
        text = match.group(1).replace("\\n", " ").strip()
        if not is_junk_feature(text, title):
            highlights.append(text)

    return list(dict.fromkeys(highlights))[:15]


def _extract_spec_tables(state: dict) -> Dict[str, str]:
    """Extract name:value spec pairs from Flipkart widget state."""
    specs = {}

    def walk(node, depth=0):
        if depth > 14:
            return
        if isinstance(node, dict):
            # Common Flipkart spec row patterns
            name = node.get("name") or node.get("key") or node.get("title")
            value = node.get("value") or node.get("val") or node.get("description")
            if isinstance(name, str) and isinstance(value, str):
                n, v = name.strip(), value.strip()
                if 2 < len(n) < 50 and 1 < len(v) < 120:
                    specs[n] = v
            for v in node.values():
                walk(v, depth + 1)
        elif isinstance(node, list):
            for item in node[:30]:
                walk(item, depth + 1)

    walk(state)
    return dict(list(specs.items())[:20])
