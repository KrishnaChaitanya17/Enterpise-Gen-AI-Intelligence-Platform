import math
import re


def calculator_tool(expression: str):

    try:
        result = eval(expression)
        return str(result)

    except Exception:
        return "Invalid calculation"


def extract_math(query: str):

    pattern = r"[0-9\.\+\-\*\/\(\) ]+"

    matches = re.findall(pattern, query)

    for m in matches:
        if any(op in m for op in ["+", "-", "*", "/"]):
            return m.strip()

    return None


async def tool_agent(query: str):

    expression = extract_math(query)

    if expression:

        result = calculator_tool(expression)

        return {
            "answer": f"Calculation result: {result}",
            "source": "tool_agent"
        }

    return {
        "answer": "No valid tool found for this query.",
        "source": "tool_agent"
    }