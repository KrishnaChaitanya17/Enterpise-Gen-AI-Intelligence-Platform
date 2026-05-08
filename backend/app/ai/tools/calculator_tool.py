import re

def calculator_tool(query: str):
    try:
        # Extract math expression safely
        expression = re.sub(r"[^0-9+\-*/(). ]", "", query)

        if not expression.strip():
            return None  # 🔥 IMPORTANT (not "Invalid")

        result = eval(expression)

        return str(result)

    except Exception:
        return None  # 🔥 IMPORTANT