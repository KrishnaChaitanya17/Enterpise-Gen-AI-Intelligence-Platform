from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.router.model_router import route_model


async def route_query_llm(query: str, plan: str = None, trace_id: str = None) -> str:

    models = route_model(query)

    llms = get_llm(models, query)

    prompt = f"""
You are a routing agent in an AI system.

Your job is to decide how to handle the user query.

Query:
{query}

Plan:
{plan}

You must choose ONE of the following routes:
- "tool" → if calculation, API, or function is needed
- "retrieval" → if knowledge lookup or RAG is needed
- "response" → if it's a greeting or simple reply

Rules:
- Output ONLY one word
- No explanation

Answer:
"""

    response = await safe_llm_call(llms, prompt, trace_id)

    route = response.content.strip().lower()

    # 🔥 Safety fallback
    if route not in ["tool", "retrieval", "response"]:
        return "retrieval"

    return route