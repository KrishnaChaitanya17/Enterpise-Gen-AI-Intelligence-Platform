import os
from app.core.env import *
from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0.0):
    model = os.getenv("CHAT_MODEL")

    # 🔒 Hard safety guard
    if not model or not model.strip():
        model = "openrouter/openai/gpt-5.2-codex"

    return ChatOpenAI(
        model=model,
        temperature=temperature,
    )


# Avoids hardcoding providers everywhere

# Makes it easy to switch OpenAI / OpenRouter / Azure later

# This is exactly how MNCs design GenAI platforms