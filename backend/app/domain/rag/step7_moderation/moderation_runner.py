from app.rag.step7_moderation.moderation_agent import moderate

def run_moderation(query: str, answer: str):
    return moderate(query, answer)
