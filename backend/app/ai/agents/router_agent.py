from typing import Literal


def route_query(query: str) -> Literal["retrieval", "reasoning", "tool"]:

    q = query.lower()

    if any(x in q for x in ["calculate", "math", "sum", "multiply"]):
        return "tool"

    if any(x in q for x in ["why", "how", "explain", "compare"]):
        return "reasoning"

    return "retrieval"