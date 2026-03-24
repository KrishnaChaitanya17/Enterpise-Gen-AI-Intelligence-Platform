BLOCKED_OUTPUT = [
    "illegal", "harmful", "dangerous"
]

def output_guard(answer: str):

    if not answer:
        return answer

    a = answer.lower()

    for word in BLOCKED_OUTPUT:
        if word in a:
            return "Response blocked due to unsafe content."

    return answer