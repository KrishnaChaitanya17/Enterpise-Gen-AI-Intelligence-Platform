# from dotenv import load_dotenv
# import os

# # Load .env
# load_dotenv()

# # Normalize keys for LangChain / OpenAI compatibility
# if os.getenv("LLM_API_KEY"):
#     os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")

# if os.getenv("LLM_API_BASE"):
#     os.environ["OPENAI_BASE_URL"] = os.getenv("LLM_API_BASE")

# # Hard fail if still missing
# if not os.getenv("OPENAI_API_KEY"):
#     raise RuntimeError("OPENAI_API_KEY not set (LLM_API_KEY missing?)")

# core/env.py
from dotenv import load_dotenv
import os

load_dotenv()

# Route OpenRouter key into OpenAI-compatible vars (ChatOpenAI only)
if os.getenv("LLM_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")

if os.getenv("LLM_API_BASE"):
    os.environ["OPENAI_API_BASE"] = os.getenv("LLM_API_BASE")
