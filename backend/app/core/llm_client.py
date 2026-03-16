import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.ai.router.model_router import route_model

load_dotenv()

def get_llm(query: str = " ",temperature: float = 0.0, streaming: bool = False,model=None):

    models = route_model(query)

    fallback_models = [
        "openai/gpt-4o-mini",
        "deepseek/deepseek-chat",
        "mistralai/mistral-7b-instruct"
    ]

    models = models + fallback_models

    api_key = os.getenv("OPENROUTER_API_KEY")
    api_base = os.getenv("OPENROUTER_API_BASE")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in environment")
    
    if model:
        models.insert(0, model)

    for m in models:
        try:
            return ChatOpenAI(
                model=m,
                temperature=temperature,
                api_key=api_key,
                base_url=api_base,   # 🔥 VERY IMPORTANT
                streaming=streaming
            )
        except Exception:
            continue
    
    raise Exception("No LLM available")


# Avoids hardcoding providers everywhere

# Makes it easy to switch OpenAI / OpenRouter / Azure later

# This is exactly how MNCs design GenAI platforms