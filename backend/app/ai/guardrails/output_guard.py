from app.ai.guardrails.pii_guard import mask_pii

BLOCKED_OUTPUT = ["illegal", "harmful", "dangerous"]


def output_guard(answer: str):

    if not answer:
        return answer, {}

    answer, pii_found = mask_pii(answer)

    a = answer.lower()

    for word in BLOCKED_OUTPUT:
        if word in a:
            return "Response blocked due to unsafe content.", {
                "unsafe_output": True,
                "pii_detected": pii_found
            }

    return answer, {
        "unsafe_output": False,
        "pii_detected": pii_found
    }