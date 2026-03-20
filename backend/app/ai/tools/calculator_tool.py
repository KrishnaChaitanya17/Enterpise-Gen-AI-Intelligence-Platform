def calculator_tool(query: str):
    try:
        # VERY SIMPLE SAFE EVAL
        expression = query.replace("calculate", "").strip()
        result = eval(expression)
        return str(result)
    except Exception:
        return "Invalid calculation"