from langchain_openai import ChatOpenAI
import os

def get_llm():
    return ChatOpenAI(
        model="mistralai/mistral-7b-instruct",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE"),
    )
