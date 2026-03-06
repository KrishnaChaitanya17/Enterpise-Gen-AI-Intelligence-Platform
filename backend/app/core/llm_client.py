import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(temperature: float = 0.0):

    model = os.getenv("CHAT_MODEL", "openai/gpt-4o-mini")
    api_key = os.getenv("OPENROUTER_API_KEY")
    api_base = os.getenv("OPENROUTER_API_BASE")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in environment")

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
        base_url=api_base,   # 🔥 VERY IMPORTANT
    )


# Avoids hardcoding providers everywhere

# Makes it easy to switch OpenAI / OpenRouter / Azure later

# This is exactly how MNCs design GenAI platforms