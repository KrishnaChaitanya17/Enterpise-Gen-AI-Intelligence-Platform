from app.core.llm_client import get_llm
from app.core.logging import logger


async def hallucination_guard(query: str, answer: str, sources: list):

    try:

        llm = get_llm()

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

        response = await llm.ainvoke(prompt)

        result = getattr(response, "content", str(response))

        return "HALLUCINATION" not in result.upper()

    except Exception as e:

        logger.warning(f"Hallucination guard failed: {e}")

        # fail-safe allow
        return True