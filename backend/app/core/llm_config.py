from app.core.env import *
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


def get_embeddings():
    return OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
    )


def get_llm(temperature: float = 0.0):
    return ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "openai/gpt-4o-mini"),
        temperature=temperature,
    )


# Avoids hardcoding providers everywhere

# Makes it easy to switch OpenAI / OpenRouter / Azure later

# This is exactly how MNCs design GenAI platforms