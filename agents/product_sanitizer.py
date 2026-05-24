"""
Sanitize scraped product data — remove nav/footer junk, infer brand from title.
"""
import re
from typing import Dict, List
from urllib.parse import urlparse, unquote

# Navigation / site chrome — NOT product features
JUNK_FEATURE_PATTERNS = [
    r"^my profile$",
    r"^orders?$",
    r"^wishlist$",
    r"^cart$",
    r"^login",
    r"^sign (in|up)",
    r"^become a seller",
    r"^flipkart plus",
    r"^rewards$",
    r"^gift cards",
    r"^help\s*center",
    r"^customer care",
    r"^notifications",
    r"^supercoin",
    r"^browse categories",
    r"^24x7 customer care",
    r"^customer support",
    r"^home$",
    r"^offers$",
    r"^sell on",
    r"^advertise",
    r"^download app",
]

JUNK_DESCRIPTION_PATTERNS = [
    r"private limited",
    r"embassy tech village",
    r"buildings alyssa",
    r"flipkart internet",
    r"copyright",
    r"all rights reserved",
    r"registered office",
    r"corporate identity",
]


def is_junk_feature(text: str, title: str = "") -> bool:
    t = text.strip().lower()
    if len(t) < 4 or len(t) > 250:
        return True
    for pat in JUNK_FEATURE_PATTERNS:
        if re.search(pat, t, re.I):
            return True

    # Cross-sell: full product listing titles from widget JSON
    if title and re.search(r"\(\w[\w\s]*,\s*\d+\s*(GB|gb|ml|L)\)", text):
        if text.strip().lower() != title.strip().lower():
            return True

    if re.match(r"^[\₹$€£]?\s*[\d,\.]+\s*$", t.strip()):
        return True
    if re.match(r"^\d{1,3}(,\d{2,3})+$", t.strip()):
        return True

    junk_phrases = [
        "complete care for your purchase",
        "compare ",
        "shop at flipkart",
        "visit the",
        "become a seller",
        "issue resolution",
        "100% refund",
        "refund",
        "warranty summary",
        "domestic warranty",
    ]
    if any(p in t for p in junk_phrases):
        return True

    if title and t == title.strip().lower():
        return True

    # Long descriptive bullets (Amazon-style) are valid features
    if len(t.split()) >= 8:
        return False

    label_only = [
        "battery type", "display size", "display type", "display features",
        "battery & power features", "other display features", "general features",
        "primary camera available", "secondary camera available",
        "primary camera", "secondary camera", "processor brand", "processor type",
    ]
    if t in label_only or (t.endswith(" features") and not re.search(r"\d", t)):
        return True

    # Short labels without substance
    has_spec_value = bool(re.search(
        r"\d|gb|tb|mb|mp\b|mah|inch|mm|ghz|core|oled|chip|camera|battery|display|"
        r"ios|5g|bluetooth|wireless|cotton|leather|polyester|wool|silk|"
        r"waterproof|washable|rechargeable|capacity|watt|ml\b|kg\b|"
        r"hardcover|paperback|pages|author|pack|pieces|fit|size",
        t, re.I,
    ))
    if not has_spec_value and len(t.split()) <= 5:
        return True

    return False


def is_junk_description(text: str) -> bool:
    if not text or len(text.strip()) < 20:
        return True
    lower = text.lower()
    for pat in JUNK_DESCRIPTION_PATTERNS:
        if re.search(pat, lower):
            return True
    return False


def infer_brand_from_title(title: str) -> str:
    """Infer brand from product title e.g. 'APPLE iPhone 17' -> 'Apple'."""
    if not title:
        return ""
    known = [
        "Apple", "Samsung", "Google", "OnePlus", "Xiaomi", "Realme", "Oppo", "Vivo",
        "Nike", "Adidas", "Sony", "LG", "Boat", "Noise", "Canon", "Nikon", "Dell",
        "HP", "Lenovo", "Asus", "MSI", "Nothing", "Motorola", "Huawei", "Honor",
        "Puma", "Reebok", "Woodland", "Redmi", "iQOO", "Titan", "Fastrack",
        "Philips", "Panasonic", "Whirlpool", "IFB", "Bosch", "Prestige", "Milton",
    ]
    title_lower = title.lower()
    for brand in known:
        if brand.lower() in title_lower:
            return brand
    # First word if all caps brand style: APPLE iPhone
    first = title.split()[0] if title.split() else ""
    if first.isupper() and len(first) > 2 and first.isalpha():
        return first.capitalize()
    return ""


def parse_title_from_url(url: str) -> str:
    """Parse product name from URL slug: apple-iphone-17-black-256-gb -> Apple iPhone 17 (Black, 256 GB)."""
    try:
        path = urlparse(url).path
        slug = path.strip("/").split("/")[0]
        if slug in ("p", "product", "dp", ""):
            return ""

        words = slug.replace("-", " ").split()
        result = []
        skip_next = False
        for i, w in enumerate(words):
            wl = w.lower()
            if wl in ("gb", "tb", "mb", "kg", "ml", "cm", "mm"):
                result.append(w.upper())
            elif wl == "iphone":
                result.append("iPhone")
            elif wl in ("5g", "4g", "3g", "wifi", "bluetooth", "usb"):
                result.append(w.upper())
            elif wl in ("pro", "max", "plus", "ultra", "lite", "se") and result:
                result.append(w.capitalize())
            elif wl in ("black", "white", "blue", "red", "green", "silver", "gold", "grey", "gray",
                        "pink", "purple", "yellow", "orange", "brown", "navy", "violet", "cobalt"):
                result.append(w.capitalize())
            else:
                result.append(w.capitalize())

        title = " ".join(result)
        # Group color + storage: "... iPhone 17 Black 256 GB" -> add parens if pattern detected
        m = re.match(
            r"^(.+?\d+)\s+(Black|White|Blue|Red|Green|Silver|Gold|Grey|Gray|Pink|Purple|"
            r"Yellow|Orange|Brown|Navy|Violet|Cobalt)\s+(\d+\s*(?:GB|TB))$",
            title, re.I,
        )
        if m:
            title = f"{m.group(1)} ({m.group(2)}, {m.group(3).upper()})"
        return title
    except Exception:
        return ""


def extract_specs_from_description(description: str, title: str = "") -> List[str]:
    """Pull feature-like phrases from a product description paragraph."""
    from agents.extractors.common import parse_description_features
    return parse_description_features(description, title)


def sanitize_product_data(product_data: Dict) -> Dict:
    """Clean scraped data before LLM enrichment and strategy."""
    title = product_data.get("title", "")
    url = product_data.get("url", "")

    # Fix title from URL if generic
    if not title or title == "Unknown Product":
        slug_title = parse_title_from_url(url)
        if slug_title:
            product_data["title"] = slug_title
            title = slug_title

    # Brand
    brand = product_data.get("brand", "")
    if not brand or brand.lower() in ("unknown", "unknown brand", "flipkart"):
        inferred = infer_brand_from_title(title)
        if inferred:
            product_data["brand"] = inferred

    # Description
    desc = product_data.get("description", "")
    if is_junk_description(desc):
        product_data["description"] = ""

    # Features — remove nav junk
    features = product_data.get("features") or []
    clean_features = [f for f in features if not is_junk_feature(f, title)]
    if not clean_features and product_data.get("description"):
        clean_features = extract_specs_from_description(product_data["description"], title)
    product_data["features"] = clean_features[:12]

    # Currency for Indian marketplaces
    domain = urlparse(url).netloc.lower()
    if "flipkart." in domain or "amazon.in" in domain:
        product_data["currency"] = product_data.get("currency") or "INR"

    product_data["scrape_quality"] = _score_scrape_quality(product_data)
    return product_data


def _score_scrape_quality(data: Dict) -> str:
    score = 0
    if data.get("title") and data["title"] not in ("Unknown Product",):
        score += 1
    if data.get("description") and not is_junk_description(data.get("description", "")):
        score += 1
    if data.get("features"):
        score += 1
    if data.get("price"):
        score += 1
    if data.get("brand") and data["brand"] not in ("Unknown", "Unknown Brand"):
        score += 1
    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"
