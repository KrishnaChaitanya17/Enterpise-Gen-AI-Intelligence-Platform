# import os
# from dotenv import load_dotenv

# load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY is not set")

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter only – OpenAI key is NOT required
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_BASE = os.getenv("LLM_API_BASE")
CHAT_MODEL = os.getenv("CHAT_MODEL")

