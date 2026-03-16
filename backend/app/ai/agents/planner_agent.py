from app.core.llm_client import get_llm


async def planner_agent(query: str):

    llm = get_llm(query)

    prompt = f"""
    Break the user request into steps.

    Query:
    {query}

    Return a list of steps required to answer it.
    """

    response = await llm.ainvoke(prompt)

    return response.content