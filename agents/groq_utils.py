"""Shared Groq API helpers."""
import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def groq_chat(
    client,
    model: str,
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1500,
    system: Optional[str] = None,
) -> Optional[str]:
    """Call Groq chat completions and return the assistant message text."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        return content.strip() if content else None
    except Exception as e:
        logger.error(f"Groq API call failed ({model}): {e}")
        return None


def parse_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse a JSON object from LLM output."""
    if not text:
        return None

    # Strip markdown fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def parse_json_array(text: str) -> list:
    """Extract and parse a JSON array from LLM output."""
    if not text:
        return []

    cleaned = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`")

    try:
        data = json.loads(cleaned)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        pass

    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return []
