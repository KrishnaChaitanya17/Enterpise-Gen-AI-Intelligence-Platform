import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import List

load_dotenv()


def get_max_tokens(query: str) -> int:
    q = query.lower()

    if "explain" in q:
        return 300
    if "code" in q:
        return 600
    return 200


def build_llm(model_name: str, query: str, temperature=0.2, streaming=False):
    """
    Build a single LLM instance
    """

    api_key = os.getenv("OPENROUTER_API_KEY")
    api_base = os.getenv("OPENROUTER_API_BASE")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
        base_url=api_base,
        streaming=streaming,
        max_tokens=get_max_tokens(query)
    )


def get_llm(model_names: List[str], query: str, temperature=0.2, streaming=False):
    """
    Convert model names → LLM instances
    """

    llms = []

    for m in model_names:
        try:
            llms.append(build_llm(m, query, temperature, streaming))
        except Exception as e:
            print(f"LLM init failed: {m} | {e}")

    return llms

# Avoids hardcoding providers everywhere

# Makes it easy to switch OpenAI / OpenRouter / Azure later

# This is exactly how MNCs design GenAI platforms