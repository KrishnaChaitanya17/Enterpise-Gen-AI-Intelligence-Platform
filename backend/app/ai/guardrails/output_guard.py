from app.ai.guardrails.pii_guard import mask_pii

def output_guard(answer: str):

    if not answer:
        return answer

    answer = mask_pii(answer)   # ✅ NEW

    BLOCKED_OUTPUT = ["illegal", "harmful", "dangerous"]

    a = answer.lower()

    for word in BLOCKED_OUTPUT:
        if word in a:
            return "Response blocked due to unsafe content."

    return answer