"""Normalize n8n / LLM responses into clean dicts."""
import json
import re
from typing import Any


def _extract_text(item: Any) -> str:
    """Try common fields where n8n stores LLM text output."""
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return ""
    for key in ("text", "output", "response", "content"):
        val = item.get(key)
        if isinstance(val, str) and val.strip():
            return val
    msg = item.get("message")
    if isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, str):
            return content
    return ""


def _strip_markdown_fences(text: str) -> str:
    return re.sub(r"```(?:json)?|```", "", text).strip()


def parse_llm_response(response_json: Any) -> dict | list | None:
    """Normalize n8n response into a parsed dict / list. Returns None if unparseable."""
    if isinstance(response_json, list) and response_json:
        item = response_json[0]
    else:
        item = response_json

    # Already structured? (extracted JD has 'role', questions has 'questions', etc)
    if isinstance(item, dict):
        if any(k in item for k in ("role", "company", "questions", "per_question", "overall")):
            return item

    raw = _extract_text(item)
    if not raw:
        return None

    cleaned = _strip_markdown_fences(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def get_debug_info(response_json: Any) -> dict:
    """Summarize response shape for debugging."""
    info: dict = {"type": type(response_json).__name__}
    if hasattr(response_json, "__len__"):
        info["length"] = len(response_json)
    if isinstance(response_json, dict):
        info["keys"] = list(response_json.keys())[:10]
    elif isinstance(response_json, list) and response_json and isinstance(response_json[0], dict):
        info["first_item_keys"] = list(response_json[0].keys())[:10]
    return info
