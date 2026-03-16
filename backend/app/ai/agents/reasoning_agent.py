from app.core.llm_client import get_llm


async def reasoning_agent(query: str):

    llm = get_llm(query)

    prompt = f"""
You are an expert AI reasoning system.

Question:
{query}

Explain step-by-step.
"""

    response = await llm.ainvoke(prompt)

    return {
        "answer": response.content,
        "source": "reasoning_agent"
    }