import os
from dotenv import load_dotenv

# Ensure env vars are loaded
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

class Config:
    @staticmethod
    def get_llm_type() -> str:
        return os.getenv("LLM_TYPE", "CLOUD").upper()

    @staticmethod
    def get_gemini_api_key() -> str | None:
        return os.getenv("GEMINI_API_KEY")

    @staticmethod
    def get_gemini_model() -> str:
        return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    @staticmethod
    def get_mongo_url() -> str:
        return os.getenv("MONGO_URL", "mongodb://localhost:27017")
