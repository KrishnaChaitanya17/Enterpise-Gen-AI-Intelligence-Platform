def route_query(query: str) -> str:
    query = query.lower().strip()

    # tool
    if any(op in query for op in ["+", "-", "*", "/", "%"]):
        return "tool"

    # greeting
    if query in ["hi", "hello", "hey"]:
        return "response"

    # default
    return "retrieval"