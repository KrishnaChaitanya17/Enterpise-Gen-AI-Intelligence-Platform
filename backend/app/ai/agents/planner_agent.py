from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.router.model_router import route_model


async def plan_task(query: str, trace_id: str = None):

    models = route_model(query)
    llms = get_llm(models, query)

    prompt = f"""
    You are a planning agent.

    Break down the following task into clear steps:

    Task: {query}
    """

    response = await safe_llm_call(llms, prompt, trace_id)

    return response.content if hasattr(response, "content") else str(response)