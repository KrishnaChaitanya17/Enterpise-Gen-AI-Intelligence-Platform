from app.core.llm_client import get_llm

_llm = None


def generate_answer(prompt: str) -> str:

    global _llm

    if _llm is None:
        _llm = get_llm(temperature=0.2)

    response = _llm.invoke(prompt)

    return response.content