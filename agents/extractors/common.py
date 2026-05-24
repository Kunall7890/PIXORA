"""Common feature extraction helpers for all e-commerce platforms."""
import re
from typing import Any, Dict, List, Optional


# Signals that a string is a real product feature (any category)
FEATURE_VALUE_SIGNALS = re.compile(
    r"\d|"
    r"\bgb\b|\btb\b|\bmb\b|\bmp\b|\bmah\b|\bml\b|\bkg\b|\bgm\b|\bl\b|\bw\b|"
    r"\binch\b|\bcm\b|\bmm\b|\bhz\b|\bwatt\b|\bhp\b|"
    r"\bbluetooth\b|\bwireless\b|\bwifi\b|\busb\b|\btype-c\b|"
    r"\bcotton\b|\bpolyester\b|\bleather\b|\bsilk\b|\bwool\b|\bdenim\b|"
    r"\bwaterproof\b|\bwashable\b|\brechargeable\b|\bcordless\b|"
    r"\bandroid\b|\bios\b|\bwindows\b|\bmacos\b|"
    r"\bstorage\b|\bbattery\b|\bcamera\b|\bdisplay\b|\bprocessor\b|\bchip\b|"
    r"\bnoise\b|\bcancelling\b|\bdriver\b|\bbass\b|\btreble\b|"
    r"\bpack\b|\bpieces\b|\bserving\b|\borganic\b|\bvegan\b|"
    r"\bfree size\b|\bslim fit\b|\bregular fit\b|\bunisex\b|"
    r"\bhardcover\b|\bpaperback\b|\bauthor\b|\bpages\b|"
    r"\bstainless\b|\bnon-stick\b|\bcapacity\b|\bvolume\b",
    re.I,
)


def specs_dict_to_features(specs: Dict[str, str], max_items: int = 12) -> List[str]:
    """Convert spec key-value pairs to feature strings."""
    features = []
    for key, val in specs.items():
        key = str(key).strip()
        val = str(val).strip()
        if not key or not val or len(key) > 60 or len(val) > 120:
            continue
        if key.lower() in ("brand", "manufacturer"):
            continue
        features.append(f"{key}: {val}")
    return features[:max_items]


def merge_feature_lists(*sources: Optional[List[str]], title: str = "", max_items: int = 12) -> List[str]:
    """Merge multiple feature lists, dedupe, prefer longer/specific entries."""
    seen = set()
    merged = []
    for source in sources:
        if not source:
            continue
        for item in source:
            text = re.sub(r"\s+", " ", str(item)).strip()
            key = text.lower()
            if not text or key in seen:
                continue
            seen.add(key)
            merged.append(text)
    return merged[:max_items]


def extract_text_from_node(node: Any) -> Optional[str]:
    """Pull display text from a nested highlight/spec node."""
    if isinstance(node, str):
        return node.strip() or None
    if isinstance(node, dict):
        for key in ("text", "value", "title", "name", "description", "content", "label"):
            v = node.get(key)
            if isinstance(v, str) and len(v.strip()) > 3:
                return v.strip()
        # name + value pair
        if node.get("name") and node.get("value"):
            return f"{node['name']}: {node['value']}"
    return None


def deep_extract_highlights(obj: Any, title: str = "", max_depth: int = 16) -> List[str]:
    """
    Walk arbitrary JSON tree and collect product highlights/spec strings.
    Works across Flipkart widgets, Amazon embedded JSON, etc.
    """
    found: List[str] = []

    def walk(node, depth=0, in_highlight_ctx=False):
        if depth > max_depth or len(found) > 30:
            return
        if isinstance(node, dict):
            ctx = in_highlight_ctx
            t1 = node.get("type", "")
            t2 = node.get("widgetType", "")
            if isinstance(t1, list):
                t1 = t1[0] if t1 else ""
            if isinstance(t2, list):
                t2 = t2[0] if t2 else ""
            node_type = (str(t1) + str(t2)).lower()
            if any(k in node_type for k in ("highlight", "spec", "feature", "attribute", "detail")):
                ctx = True

            for key in ("highlights", "keySpecs", "key_specs", "specifications", "attributes",
                        "productHighlights", "listingSummary", "featureBullets", "features"):
                val = node.get(key)
                if isinstance(val, list):
                    for item in val:
                        text = extract_text_from_node(item)
                        if text:
                            found.append(text)
                        elif isinstance(item, dict):
                            walk(item, depth + 1, True)

            # name/value spec row
            text = extract_text_from_node(node)
            if text and ctx and _looks_like_feature_text(text, title):
                found.append(text)

            for k, v in node.items():
                if k in ("image", "images", "media", "tracking", "action", "url"):
                    continue
                walk(v, depth + 1, ctx)

        elif isinstance(node, list):
            for item in node[:40]:
                walk(item, depth + 1, in_highlight_ctx)

    walk(obj)
    return found


def _looks_like_feature_text(text: str, title: str = "") -> bool:
    from agents.product_sanitizer import is_junk_feature
    if is_junk_feature(text, title):
        return False
    if len(text) < 8:
        return False
    # Accept spec-style "Key: Value" or strings with product signals
    if ":" in text and len(text.split(":")[0]) < 40:
        return True
    return bool(FEATURE_VALUE_SIGNALS.search(text))


def parse_description_features(description: str, title: str = "") -> List[str]:
    """Extract feature phrases from marketplace SEO descriptions."""
    if not description:
        return []

    features = []
    patterns = [
        r"(?:include|includes|features?|specifications?|specs?)\s+(.+?)(?:\.|compare|buy|shop|$)",
        r"(?:with|featuring)\s+(.+?)(?:\.|compare|buy|shop|$)",
    ]
    for pat in patterns:
        match = re.search(pat, description, re.I | re.DOTALL)
        if match:
            chunk = match.group(1)
            parts = re.split(r",|\band\b|\|", chunk)
            for p in parts:
                p = re.sub(r"\s+", " ", p).strip(" .")
                if 5 < len(p) < 150:
                    from agents.product_sanitizer import is_junk_feature
                    if not is_junk_feature(p, title):
                        features.append(p)

    return list(dict.fromkeys(features))[:12]
