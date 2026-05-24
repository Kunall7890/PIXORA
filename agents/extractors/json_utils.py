"""Shared JSON extraction helpers for e-commerce embedded state."""
import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def extract_balanced_json(html: str, marker: str, max_chars: int = 4_000_000) -> Optional[dict]:
    """Extract a JSON object assigned after a JS marker like window.__INITIAL_STATE__ = """
    idx = html.find(marker)
    if idx < 0:
        return None
    start = html.find("{", idx)
    if start < 0:
        return None
    depth = 0
    end = start
    limit = min(len(html), start + max_chars)
    for i, ch in enumerate(html[start:limit], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    try:
        return json.loads(html[start:end])
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed for {marker}: {e}")
        return None


def deep_find_key(obj: Any, target_keys: set, max_depth: int = 14) -> List[Any]:
    """Find all values for keys anywhere in nested JSON."""
    found = []

    def walk(node, depth=0):
        if depth > max_depth or len(found) > 50:
            return
        if isinstance(node, dict):
            for k, v in node.items():
                if k in target_keys:
                    found.append(v)
                walk(v, depth + 1)
        elif isinstance(node, list):
            for item in node[:40]:
                walk(item, depth + 1)

    walk(obj)
    return found


def collect_strings(obj: Any, min_len: int = 8, max_len: int = 220, max_depth: int = 12) -> List[str]:
    """Collect string leaf values from nested JSON."""
    out = []

    def walk(node, depth=0):
        if depth > max_depth or len(out) > 200:
            return
        if isinstance(node, str) and min_len <= len(node) <= max_len:
            out.append(node.strip())
        elif isinstance(node, dict):
            for v in node.values():
                walk(v, depth + 1)
        elif isinstance(node, list):
            for item in node[:30]:
                walk(item, depth + 1)

    walk(obj)
    return out
