from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.router.model_router import route_model
from app.core.logging import logger


async def hallucination_guard(query: str, answer: str, sources: list, trace_id: str = None):

    try:

        models = route_model(query)
        llms = get_llm(models,query)
 
        prompt = f"""
You are an AI safety system.

Determine if the answer is grounded in the provided sources.

User Question:
{query}

Model Answer:
{answer}

Sources:
{sources}

Respond ONLY with:
SAFE
or
HALLUCINATION
"""

        response = await safe_llm_call(llms, prompt, trace_id)

        result = getattr(response, "content", str(response))

        return "HALLUCINATION" not in result.upper()

    except Exception as e:

        logger.warning(f"Hallucination guard failed: {e}")

        # fail-safe allow
        return True