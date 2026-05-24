"""
Product Research Agent — universal Flipkart & Amazon extraction
"""
import json
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

from agents.extractors.router import detect_platform, extract_platform_data, is_blocked_page
from agents.extractors.common import merge_feature_lists, parse_description_features, specs_dict_to_features
from agents.product_sanitizer import sanitize_product_data, parse_title_from_url

logger = logging.getLogger(__name__)

SITE_TAGLINE_PATTERNS = [
    r"free shipping", r"shop now", r"best deals", r"online store",
    r"official (site|store|website)", r"buy online", r"welcome to",
]


class ProductResearchAgent:
    """Scrapes and extracts product data from e-commerce URLs"""

    def __init__(self):
        self.timeout = 35
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    async def extract_product_info(self, url: str) -> Dict:
        try:
            logger.info(f"Researching product: {url}")
            platform = detect_platform(url)

            html_content = await self._fetch_page(url, platform)
            if not html_content:
                return self._fallback_from_url(url)

            # Platform-specific extraction (Flipkart / Amazon)
            structured = extract_platform_data(html_content, url) or {}

            soup = BeautifulSoup(html_content, "html.parser")
            if not structured:
                structured = self._extract_json_ld_product(soup)

            domain = urlparse(url).netloc.lower()
            title = structured.get("title") or self._extract_title(soup, domain) or parse_title_from_url(url)

            description = structured.get("description") or self._extract_product_description(
                soup, structured, title, domain
            )

            specs = structured.get("specs") or self._extract_specs(soup)
            spec_features = specs_dict_to_features(specs)

            features = merge_feature_lists(
                structured.get("features"),
                spec_features,
                parse_description_features(description, title),
                self._extract_features(soup, domain),
                title=title,
            )

            product_data = {
                "url": url,
                "title": title,
                "description": description,
                "price": structured.get("price") or self._extract_price(soup, domain),
                "currency": structured.get("currency") or self._extract_currency(soup, domain),
                "features": features,
                "specs": specs,
                "reviews_summary": structured.get("reviews") or self._extract_reviews(soup),
                "rating": structured.get("rating") or self._extract_rating(soup),
                "image_urls": structured.get("image_urls") or self._extract_images(soup, url),
                "brand": structured.get("brand") or self._extract_brand(soup, url, title),
                "page_text": self._build_page_text(title, description, features, specs),
                "platform": platform,
            }

            product_data = sanitize_product_data(product_data)

            # If no features after extraction, seed from title for enrichment
            if not product_data.get("features") and product_data.get("title"):
                product_data["features"] = _title_hint_features(product_data["title"])
            logger.info(
                f"✓ Extracted [{platform}]: {product_data['title']} | "
                f"{len(product_data.get('features', []))} features | quality={product_data.get('scrape_quality')}"
            )
            return product_data

        except Exception as e:
            logger.error(f"Error extracting product info: {str(e)}")
            return self._fallback_from_url(url)

    async def _fetch_page(self, url: str, platform: str) -> Optional[str]:
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Sec-Ch-Ua": '"Chromium";v="120", "Google Chrome";v="120", "Not_A Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

        # Fast httpx fetch (works for Amazon; Flipkart when not captcha-blocked)
        html = await self._httpx_fetch(url, headers)
        # Flipkart mobile/deep link fallback when blocked
        if platform == "flipkart" and html and is_blocked_page(html, platform):
            parsed = urlparse(url)
            mobile_url = url.replace("://www.", "://m.").replace("://dl.", "://m.")
            if mobile_url != url:
                logger.info(f"Retrying Flipkart mobile URL")
                mobile_html = await self._httpx_fetch(mobile_url, headers)
                if mobile_html and not is_blocked_page(mobile_html, platform):
                    return mobile_html

        # Amazon bot pages are tiny — retry mobile product URL
        if platform == "amazon" and html and len(html) < 80000:
            asin_match = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", url)
            if asin_match:
                mobile_url = f"https://www.amazon.in/gp/aw/d/{asin_match.group(1)}"
                logger.info(f"Retrying Amazon mobile URL: {mobile_url}")
                mobile_html = await self._httpx_fetch(mobile_url, headers)
                if mobile_html and len(mobile_html) > len(html or ""):
                    html = mobile_html

        if html and not is_blocked_page(html, platform):
            return html

        # Playwright fallback for JS-rendered / bot-blocked pages
        if HAS_PLAYWRIGHT:
            logger.info(f"Retrying with Playwright for {platform}: {url[:60]}")
            html = await self._playwright_fetch(url)
            if html and not is_blocked_page(html, platform):
                return html

        # Return partial HTML for URL-slug + LLM enrichment fallback
        return html

    async def _httpx_fetch(self, url: str, headers: dict) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.text
                logger.warning(f"HTTP {response.status_code} for {url[:60]}")
        except Exception as e:
            logger.warning(f"httpx fetch failed: {e}")
        return None

    async def _playwright_fetch(self, url: str) -> Optional[str]:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.user_agent,
                    locale="en-IN",
                    viewport={"width": 1280, "height": 900},
                )
                page = await context.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
                await page.wait_for_timeout(4000)
                content = await page.content()
                await browser.close()
                return content
        except Exception as e:
            logger.warning(f"Playwright fetch failed: {e}")
        return None

    def _fallback_from_url(self, url: str) -> Dict:
        title = parse_title_from_url(url)
        return sanitize_product_data({
            "url": url,
            "title": title or "Product Unavailable",
            "description": "",
            "price": None,
            "currency": "INR" if "flipkart" in url or "amazon.in" in url else "USD",
            "features": [],
            "specs": {},
            "reviews_summary": None,
            "rating": None,
            "image_urls": [],
            "brand": "",
            "page_text": f"Title: {title}" if title else "",
            "platform": detect_platform(url),
        })

    def _build_page_text(self, title, description, features, specs) -> str:
        chunks = []
        if title:
            chunks.append(f"Title: {title}")
        if description:
            chunks.append(f"Description: {description[:1500]}")
        for f in (features or [])[:10]:
            chunks.append(f"Feature: {f}")
        for k, v in list((specs or {}).items())[:10]:
            chunks.append(f"{k}: {v}")
        return "\n".join(chunks)[:4000]

    def _is_site_tagline(self, text: str, title: str = "") -> bool:
        if not text or len(text.strip()) < 15:
            return True
        lower = text.lower().strip()
        for pattern in SITE_TAGLINE_PATTERNS:
            if re.search(pattern, lower):
                return True
        title_words = {w for w in re.findall(r"\w+", (title or "").lower()) if len(w) > 3}
        if title_words:
            overlap = sum(1 for w in title_words if w in lower)
            if overlap == 0 and len(lower) < 120:
                return True
        return False

    def _extract_product_description(
        self, soup: BeautifulSoup, structured: Dict, title: str, domain: str
    ) -> str:
        if structured.get("description"):
            return structured["description"][:2000]

        candidates = []
        for el in soup.select('[itemprop="description"]'):
            text = el.get("content") or el.get_text(" ", strip=True)
            if text:
                candidates.append(text)

        for sel in ["#productDescription", ".product-description", ".product__description"]:
            for el in soup.select(sel):
                text = el.get_text(" ", strip=True)
                if text and len(text) > 30:
                    candidates.append(text)

        for meta in [soup.find("meta", property="og:description"), soup.find("meta", attrs={"name": "description"})]:
            if meta and meta.get("content"):
                candidates.append(meta["content"])

        for text in candidates:
            cleaned = re.sub(r"\s+", " ", text).strip()
            if len(cleaned) > 25 and not self._is_site_tagline(cleaned, title):
                return cleaned[:2000]

        return ""

    def _extract_title(self, soup: BeautifulSoup, domain: str) -> str:
        for sel in ["#productTitle", "span.B_NuCI", "h1"]:
            el = soup.select_one(sel)
            if el:
                t = el.get_text(strip=True)
                if t and len(t) > 3:
                    return t
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            return og["content"]
        return ""

    def _extract_price(self, soup: BeautifulSoup, domain: str) -> Optional[float]:
        for sel in [".a-price .a-offscreen", "span[class*='price']", "motion[class*='price']"]:
            el = soup.select_one(sel)
            if el:
                match = re.search(r"[\d,]+\.?\d*", el.get_text().replace(",", ""))
                if match:
                    try:
                        return float(match.group())
                    except ValueError:
                        pass
        meta = soup.find("meta", property="product:price:amount")
        if meta and meta.get("content"):
            try:
                return float(meta["content"])
            except ValueError:
                pass
        return None

    def _extract_currency(self, soup: BeautifulSoup, domain: str = "") -> str:
        tag = soup.find("meta", property="product:price:currency")
        if tag and tag.get("content"):
            return tag["content"]
        html = str(soup)[:80000]
        for sym, code in [("₹", "INR"), ("$", "USD"), ("€", "EUR"), ("£", "GBP")]:
            if sym in html:
                return code
        return "INR" if domain and ("flipkart" in domain or "amazon.in" in domain) else "USD"

    def _extract_features(self, soup: BeautifulSoup, domain: str) -> List[str]:
        features = []
        for li in soup.select("#feature-bullets li span.a-list-item, ul li"):
            t = li.get_text(strip=True)
            if 8 < len(t) < 220:
                features.append(t)
        return list(dict.fromkeys(features))[:12]

    def _extract_specs(self, soup: BeautifulSoup) -> Dict[str, str]:
        specs = {}
        for row in soup.select("table tr, #productOverview_feature_div tr"):
            cols = row.find_all(["td", "th"])
            if len(cols) >= 2:
                key = cols[0].get_text(strip=True)
                val = cols[1].get_text(strip=True)
                if key and val and len(key) < 50:
                    specs[key] = val
        return specs

    def _extract_reviews(self, soup: BeautifulSoup) -> Optional[str]:
        el = soup.select_one("#acrCustomerReviewText, [data-hook='total-review-count']")
        return el.get_text(strip=True) if el else None

    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        for el in soup.select("#acrPopover, [data-hook='rating-out-of-text']"):
            match = re.search(r"(\d+\.?\d*)", el.get("title", "") + el.get_text())
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        return None

    def _extract_json_ld_product(self, soup: BeautifulSoup) -> Dict:
        result = {}
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") in ("Product", "IndividualProduct"):
                        if item.get("name"):
                            result["title"] = item["name"]
                        if item.get("description"):
                            result["description"] = item["description"]
            except (json.JSONDecodeError, TypeError):
                continue
        return result

    def _extract_images(self, soup: BeautifulSoup, url: str = "") -> List[str]:
        images = []
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            images.append(og["content"])
        for img in soup.select("#landingImage, img[src*='http']"):
            src = img.get("src") or img.get("data-src")
            if src and src.startswith("http"):
                images.append(src)
        return list(dict.fromkeys(images))[:10]

    def _extract_brand(self, soup: BeautifulSoup, url: str = "", title: str = "") -> str:
        from agents.product_sanitizer import infer_brand_from_title
        inferred = infer_brand_from_title(title)
        if inferred:
            return inferred
        el = soup.select_one("#bylineInfo, [itemprop='brand']")
        if el:
            return el.get_text(strip=True)
        return ""


product_researcher = ProductResearchAgent()


def _title_hint_features(title: str) -> List[str]:
    """Minimal feature hints parsed from product title when page is blocked."""
    hints = []
    if not title:
        return hints
    hints.append(f"Product: {title}")
    for spec in re.findall(r"\d+\s*(?:GB|TB|MB|MP|mAh|inch|W|Kg|ml)\b", title, re.I):
        hints.append(spec)
    for color in re.findall(
        r"\((Black|White|Blue|Red|Green|Silver|Gold|Grey|Gray|Pink|Purple|Yellow|Orange|Brown|Navy|Violet|Cobalt)",
        title, re.I,
    ):
        hints.append(f"Color: {color}")
    return hints[:6]

