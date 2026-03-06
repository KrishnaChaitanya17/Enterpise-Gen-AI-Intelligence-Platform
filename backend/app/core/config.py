from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "Enterprise AI Platform"
    ENV: str = "development"

    # Database
    MONGODB_URI: str

    # Security
    SECRET_KEY: str

    # OpenRouter / LLM
    OPENROUTER_API_KEY: str
    OPENROUTER_API_BASE: str

    LLM_API_KEY: str
    LLM_API_BASE: str
    CHAT_MODEL: str
    EMBEDDING_MODEL: str

    model_config = {
        "env_file": ".env",
        "extra": "ignore"   # Prevent future crashes if new env vars added
    }


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()