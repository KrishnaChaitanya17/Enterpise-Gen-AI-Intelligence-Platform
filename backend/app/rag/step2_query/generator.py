import os
from app.core.env import *   # ensures env vars are loaded
from langchain_openai import ChatOpenAI

def generate_answer(prompt: str) -> str:
    llm = ChatOpenAI(
        model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        temperature=0.2
    )
    return llm.invoke(prompt).content
