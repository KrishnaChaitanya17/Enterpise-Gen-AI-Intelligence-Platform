from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.router.model_router import route_model


async def reasoning_agent(query: str, trace_id = None):

    models = route_model(query)
    llms = get_llm(models, query)

    prompt = f"""
You are an expert AI reasoning system.

Question:
{query}

Explain step-by-step.
"""

    response = await safe_llm_call(llms, prompt, trace_id)

    return {
        "answer": response.content,
        "source": "reasoning_agent"
    }