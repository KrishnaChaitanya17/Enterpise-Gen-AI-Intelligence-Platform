from app.ai.tools.calculator_tool import calculator_tool

TOOLS = {
    "calculator": calculator_tool
}

def get_tool(tool_name: str):
    return TOOLS.get(tool_name)