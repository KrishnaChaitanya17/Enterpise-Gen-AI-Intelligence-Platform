from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.router.model_router import route_model

async def generate_answer(prompt: str, trace_id=None) -> str:

    models = route_model(prompt)
    llms = get_llm(models, prompt)

    response = await safe_llm_call(llms, prompt, trace_id)

    return getattr(response, "content", "")