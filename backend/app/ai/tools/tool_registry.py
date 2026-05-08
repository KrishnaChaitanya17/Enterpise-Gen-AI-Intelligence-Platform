from app.ai.tools.calculator_tool import calculator_tool

TOOLS = {
    "calculator": calculator_tool
}


def get_tool(tool_name: str):
    return TOOLS.get(tool_name)


# 🔥 NEW: dynamic tool selection
async def select_tool(query: str) -> str:
    q = query.lower()

    if any(op in q for op in ["+", "-", "*", "/"]):
        return "calculator"

    # future tools can be added here
    return None