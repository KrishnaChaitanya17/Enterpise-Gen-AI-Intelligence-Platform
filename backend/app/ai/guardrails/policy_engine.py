RULES = {
    "block_input": True,
    "block_output": True,
    "mask_pii": True,
    "block_hallucination": True
}


def evaluate_policy(context: dict):
    """
    Central decision engine
    """

    decisions = {
        "allow": True,
        "reason": None
    }

    # 🔴 Block unsafe input
    if context.get("input_blocked") and RULES["block_input"]:
        decisions["allow"] = False
        decisions["reason"] = "Unsafe input detected"

    # 🔴 Block hallucination
    if context.get("hallucination") and RULES["block_hallucination"]:
        decisions["allow"] = False
        decisions["reason"] = "Hallucination detected"

    # 🔴 Block unsafe output
    if context.get("unsafe_output") and RULES["block_output"]:
        decisions["allow"] = False
        decisions["reason"] = "Unsafe output"

    return decisions