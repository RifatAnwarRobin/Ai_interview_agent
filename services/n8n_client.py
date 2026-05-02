"""Low-level HTTP communication with n8n webhooks."""
import requests
from typing import Any

from services.config import config


class N8NError(Exception):
    """Raised for any webhook / connection failure."""


def post_webhook(endpoint: str, payload: dict, timeout: int | None = None) -> Any:
    """POST a JSON payload to an n8n endpoint. Returns parsed JSON.

    `endpoint` is the path segment after the base URL — e.g. 'gather', 'questions'.
    """
    url = f"{config.WEBHOOK_BASE_URL}/{endpoint.lstrip('/')}"
    timeout = timeout or config.REQUEST_TIMEOUT_EXTRACT

    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.exceptions.Timeout:
        raise N8NError(f"n8n took longer than {timeout}s to respond.")
    except requests.exceptions.ConnectionError:
        raise N8NError(
            "Could not reach n8n. Is it running? "
            "Did you click 'Execute workflow' on the canvas (test mode)?"
        )
    except requests.exceptions.RequestException as e:
        raise N8NError(f"Request failed: {e}")

    if response.status_code != 200:
        raise N8NError(f"n8n returned HTTP {response.status_code}: {response.text[:200]}")

    try:
        return response.json()
    except ValueError:
        raise N8NError(f"n8n response was not valid JSON: {response.text[:200]}")


def ping_webhook(endpoint: str = "gather") -> tuple[bool, str]:
    """Best-effort liveness check against an endpoint. Returns (ok, message)."""
    try:
        post_webhook(endpoint, {"_ping": True}, timeout=5)
        return True, "Connected"
    except N8NError as e:
        return False, str(e)
