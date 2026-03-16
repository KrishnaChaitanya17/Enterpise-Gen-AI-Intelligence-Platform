from app.ai.agents.tool_agent import calculator

TOOLS = {
    "calculator" : calculator
}

def get_tool(tool_name: str):
    return TOOLS.get(tool_name)