# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     # LLM (generation)
#     llm_api_key: str
#     llm_api_base: str
#     chat_model: str

#     # Embeddings
#     embedding_model: str

#     class Config:
#         env_file = ".env"
#         extra = "forbid"

# settings = Settings()

from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Normalize keys for LangChain / OpenAI compatibility
if os.getenv("LLM_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")

if os.getenv("LLM_API_BASE"):
    os.environ["OPENAI_BASE_URL"] = os.getenv("LLM_API_BASE")

# Hard fail if still missing
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set (LLM_API_KEY missing?)")
