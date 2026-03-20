async def tool_agent(query: str):
    from app.ai.tools.tool_registry import get_tool

    if "calculate" in query or "+" in query or "*" in query:

        tool = get_tool("calculator")

        result = tool(query)

        return {
            "answer": result,
            "tool_used": "calculator"
        }

    return {
        "answer": None,
        "tool_used": None
    }