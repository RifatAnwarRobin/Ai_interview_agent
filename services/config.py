"""Central configuration. Loads env vars once, exposes constants."""
# import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # WEBHOOK_BASE_URL: str = os.getenv(
    #     "N8N_WEBHOOK_URL",
    #     "http://localhost:5678/webhook-test",
    # )
    # MISTRAL_KEY: str = os.getenv("MISTRAL_KEY", "")
    # REQUEST_TIMEOUT_EXTRACT: int = int(os.getenv("REQUEST_TIMEOUT_EXTRACT", "60"))
    # REQUEST_TIMEOUT_QUESTIONS: int = int(os.getenv("REQUEST_TIMEOUT_QUESTIONS", "60"))
    # REQUEST_TIMEOUT_EVALUATE: int = int(os.getenv("REQUEST_TIMEOUT_EVALUATE", "120"))

    WEBHOOK_BASE_URL: str = "http://localhost:5678/webhook-test"
    MISTRAL_KEY: str = ""
    REQUEST_TIMEOUT_EXTRACT: int = 60
    REQUEST_TIMEOUT_QUESTIONS: int = 60
    REQUEST_TIMEOUT_EVALUATE: int = 120
    
    APP_NAME: str = "Interview Copilot"
    APP_TAGLINE: str = "AI-powered interview preparation"
    VERSION: str = "0.1.0"


config = Config()
