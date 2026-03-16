import re

def route_model(query: str):

    q = query.lower()

    code_patterns = [
        "code",
        "python",
        "javascript",
        "react",
        "api",
        "algorithm",
        "sql"
    ]

    reasoning_patterns = [
        "why",
        "how",
        "explain",
        "compare",
        "difference",
        "analysis"
    ]

    for p in code_patterns:
        if p in q:
            return ["deepseek/deepseek-coder"]

    for p in reasoning_patterns:
        if p in q:
            return ["openai/gpt-4o"]

    return ["openai/gpt-4o-mini"]