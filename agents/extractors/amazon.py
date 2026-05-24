"""Amazon.in / Amazon.com product page extractor."""
import json
import logging
import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from agents.extractors.common import (
    deep_extract_highlights,
    merge_feature_lists,
    parse_description_features,
    specs_dict_to_features,
)

logger = logging.getLogger(__name__)


def extract_amazon_product(html: str, url: str = "") -> Optional[Dict]:
    """Extract product data from Amazon product detail page HTML."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        result: Dict = {}

        # Title
        for sel in ["#productTitle", "#title", "h1#title"]:
            el = soup.select_one(sel)
            if el:
                result["title"] = el.get_text(strip=True)
                break

        if not result.get("title"):
            og = soup.find("meta", property="og:title")
            if og and og.get("content"):
                result["title"] = og["content"]

        # Brand
        byline = soup.select_one("#bylineInfo, a#brand, .po-brand .po-break-word")
        if byline:
            brand_text = byline.get_text(strip=True)
            brand_text = re.sub(r"^(Visit the|Brand:\s*|Store:\s*)", "", brand_text, flags=re.I).strip()
            if brand_text and "amazon" not in brand_text.lower():
                result["brand"] = brand_text.split(" Store")[0].strip()

        # Price
        for sel in [
            "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
            "#corePrice_feature_div .a-price .a-offscreen",
            ".a-price .a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "span.a-price-whole",
        ]:
            el = soup.select_one(sel)
            if el:
                price = _parse_price(el.get_text())
                if price:
                    result["price"] = price
                    break

        # Currency
        if "amazon.in" in url or "₹" in html[:50000]:
            result["currency"] = "INR"
        elif "amazon.co.uk" in url or "£" in html[:50000]:
            result["currency"] = "GBP"
        elif "€" in html[:50000]:
            result["currency"] = "EUR"
        else:
            result["currency"] = "USD"

        # Rating
        for sel in ["#acrPopover", "span#acrPopover", "i.a-icon-star span"]:
            el = soup.select_one(sel)
            if el:
                match = re.search(r"(\d+\.?\d*)\s*out of", el.get("title", "") + el.get_text())
                if match:
                    result["rating"] = float(match.group(1))
                    break
        rating_el = soup.select_one("[data-hook='rating-out-of-text']")
        if rating_el and not result.get("rating"):
            match = re.search(r"(\d+\.?\d*)", rating_el.get_text())
            if match:
                result["rating"] = float(match.group(1))

        review_el = soup.select_one("#acrCustomerReviewText, [data-hook='total-review-count']")
        if review_el:
            result["reviews"] = review_el.get_text(strip=True)

        # Description
        desc_parts = []
        for sel in ["#productDescription p", "#productDescription_feature_div p", "#aplus_feature_div p"]:
            for p in soup.select(sel)[:8]:
                t = p.get_text(" ", strip=True)
                if t and len(t) > 30:
                    desc_parts.append(t)
        if desc_parts:
            result["description"] = " ".join(desc_parts)[:2000]

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content") and not result.get("description"):
            result["description"] = meta_desc["content"]

        # Feature bullets — primary source
        bullets = []
        for li in soup.select("#feature-bullets li span.a-list-item"):
            t = li.get_text(strip=True)
            if t and not t.lower().startswith("note:"):
                bullets.append(t)

        # Product overview table (quick specs)
        specs = {}
        for row in soup.select(
            "#productOverview_feature_div tr, #poExpander tr, "
            "table.prodDetTable tr, .a-expander-content tr"
        ):
            cols = row.find_all(["td", "th"])
            if len(cols) >= 2:
                key = cols[0].get_text(strip=True)
                val = cols[1].get_text(strip=True)
                if key and val and len(key) < 50:
                    specs[key] = val

        if specs:
            result["specs"] = specs

        spec_features = specs_dict_to_features(specs)
        overview_features = []
        for row in soup.select("#productOverview_feature_div tr")[:8]:
            cols = row.find_all(["td", "th"])
            if len(cols) >= 2:
                overview_features.append(
                    f"{cols[0].get_text(strip=True)}: {cols[1].get_text(strip=True)}"
                )

        # JSON-LD
        json_ld = _extract_json_ld(soup)
        if json_ld:
            if json_ld.get("title") and not result.get("title"):
                result["title"] = json_ld["title"]
            if json_ld.get("description") and not result.get("description"):
                result["description"] = json_ld["description"]
            if json_ld.get("brand") and not result.get("brand"):
                result["brand"] = json_ld["brand"]
            if json_ld.get("price") and not result.get("price"):
                result["price"] = json_ld["price"]
            if json_ld.get("rating") and not result.get("rating"):
                result["rating"] = json_ld["rating"]
            if json_ld.get("image_urls"):
                result["image_urls"] = json_ld["image_urls"]

        # Embedded JSON highlights
        embedded = _extract_embedded_json_highlights(html, result.get("title", ""))

        desc_features = parse_description_features(
            result.get("description", ""), result.get("title", "")
        )

        result["features"] = merge_feature_lists(
            bullets,
            overview_features,
            spec_features,
            embedded,
            desc_features,
            title=result.get("title", ""),
        )

        # Images
        if not result.get("image_urls"):
            imgs = []
            for sel in ["#landingImage", "#imgTagWrapperId img", "#main-image"]:
                el = soup.select_one(sel)
                if el and el.get("src"):
                    imgs.append(el["src"])
            og_img = soup.find("meta", property="og:image")
            if og_img and og_img.get("content"):
                imgs.append(og_img["content"])
            result["image_urls"] = list(dict.fromkeys(imgs))[:8]

        if result.get("title"):
            logger.info(f"Amazon extracted: {result['title'][:60]}")
            return result
        return None

    except Exception as e:
        logger.warning(f"Amazon extraction failed: {e}")
        return None


def _parse_price(text: str) -> Optional[float]:
    try:
        clean = re.sub(r"[^\d.]", "", text.replace(",", ""))
        return float(clean) if clean else None
    except (ValueError, TypeError):
        return None


def _extract_json_ld(soup: BeautifulSoup) -> Dict:
    result = {}
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") not in ("Product", "IndividualProduct"):
                    continue
                if item.get("name"):
                    result["title"] = item["name"]
                if item.get("description"):
                    result["description"] = item["description"]
                brand = item.get("brand")
                if isinstance(brand, dict):
                    result["brand"] = brand.get("name", "")
                elif isinstance(brand, str):
                    result["brand"] = brand
                offers = item.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                if isinstance(offers, dict) and offers.get("price"):
                    try:
                        result["price"] = float(str(offers["price"]).replace(",", ""))
                    except (ValueError, TypeError):
                        pass
                rating = item.get("aggregateRating", {})
                if isinstance(rating, dict) and rating.get("ratingValue"):
                    try:
                        result["rating"] = float(rating["ratingValue"])
                    except (ValueError, TypeError):
                        pass
                images = item.get("image", [])
                if isinstance(images, str):
                    result["image_urls"] = [images]
                elif isinstance(images, list):
                    result["image_urls"] = [i for i in images if isinstance(i, str)]
        except (json.JSONDecodeError, TypeError):
            continue
    return result


def _extract_embedded_json_highlights(html: str, title: str) -> List[str]:
    """Parse feature bullets from Amazon inline JSON blobs."""
    highlights = []
    for match in re.finditer(r'"featureBullets"\s*:\s*(\[.*?\])', html, re.DOTALL):
        try:
            bullets = json.loads(match.group(1))
            for b in bullets:
                if isinstance(b, str):
                    highlights.append(b)
                elif isinstance(b, dict) and b.get("text"):
                    highlights.append(b["text"])
        except json.JSONDecodeError:
            continue

    # Generic deep walk on large script blocks
    for script_match in re.finditer(r"<script[^>]*>(.*?)</script>", html, re.DOTALL):
        content = script_match.group(1)
        if len(content) < 500 or "productTitle" not in content:
            continue
        try:
            if content.strip().startswith("{"):
                data = json.loads(content)
                highlights.extend(deep_extract_highlights(data, title))
        except json.JSONDecodeError:
            pass

    return highlights[:15]
