"""High-level API operations. One function per business action."""
from services.n8n_client import post_webhook
from services.parser import parse_llm_response
from services.config import config


def extract_jd(jd_text: str, difficulty: str, input_type: str = "Job Interview") -> dict | None:
    """Send Job Description text to n8n /gather, return parsed Job Description dict (or None on parse failure)."""
    response = post_webhook(
        endpoint="gather",
        payload={
            "input_type": input_type,
            "difficulty": difficulty,
            "jd_text": jd_text.strip(),
        },
        timeout=config.REQUEST_TIMEOUT_EXTRACT,
    )
    return parse_llm_response(response)


def generate_questions(jd_data: dict, difficulty: str, count: int) -> list[dict] | None:
    """Send Job Description data to n8n /questions, return list of question dicts (or None)."""
    response = post_webhook(
        endpoint="questions",
        payload={
            "jd_data": jd_data,
            "difficulty": difficulty,
            "question_count": count,
        },
        timeout=config.REQUEST_TIMEOUT_QUESTIONS,
    )
    parsed = parse_llm_response(response)
    if isinstance(parsed, dict):
        return parsed.get("questions", [])
    if isinstance(parsed, list):
        return parsed
    return None


def evaluate_answers(jd_data: dict, qa_pairs: list[dict]) -> dict | None:
    """Send Q&A pairs to n8n /evaluate, return evaluation dict (or None)."""
    response = post_webhook(
        endpoint="evaluate",
        payload={
            "user_id": "demo_user",
            "jd_data": jd_data,
            "answers": qa_pairs,
        },
        timeout=config.REQUEST_TIMEOUT_EVALUATE,
    )
    return parse_llm_response(response)
