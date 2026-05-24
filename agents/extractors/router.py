"""Route URL to the correct platform extractor."""
import logging
import re
from typing import Dict, Optional
from urllib.parse import urlparse

from agents.extractors.amazon import extract_amazon_product
from agents.extractors.flipkart import extract_flipkart_product

logger = logging.getLogger(__name__)


def detect_platform(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if "flipkart." in domain:
        return "flipkart"
    if "amazon." in domain:
        return "amazon"
    return "generic"


def is_blocked_page(html: str, platform: str = "") -> bool:
    """Detect bot-block / captcha pages — avoid false positives on normal product pages."""
    min_size = 80000 if platform in ("amazon", "flipkart") else 5000
    if not html or len(html) < min_size:
        return True

    head = html[:8000].lower()

    # Flipkart captcha page is tiny
    if len(html) < 5000 and "recaptcha" in head:
        return True

    title_match = re.search(r"<title[^>]*>([^<]+)</title>", head, re.I)
    title = title_match.group(1).lower() if title_match else ""

    if any(s in title for s in ("captcha", "robot check", "access denied", "blocked")):
        return True

    if "flipkart recaptcha" in title or "are you a human" in head:
        return True

    if "sorry, we just need to make sure you're not a robot" in html.lower():
        return True

    return False


def extract_platform_data(html: str, url: str) -> Optional[Dict]:
    """Run platform-specific extractor. Returns None if blocked or unsupported."""
    platform = detect_platform(url)
    if is_blocked_page(html, platform):
        logger.warning(f"Blocked/partial page detected for: {url[:80]} ({len(html or '')} bytes)")
        return None
    if platform == "flipkart":
        return extract_flipkart_product(html)
    if platform == "amazon":
        return extract_amazon_product(html, url)

    return None
