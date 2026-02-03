# #Judge agent (multi-claim reasoning)

# from app.rag.step4_verification.claim_extractor import extract_claims
# from app.rag.step4_verification.decision_engine import evaluate_claims


# def verify_answer(answer: str, docs: list) -> dict:
#     """
#     Step 4:
#     - Break answer into claims
#     - Verify each claim against retrieved docs
#     - Produce verdict
#     """

#     claims = extract_claims(answer)
#     checks = evaluate_claims(claims, docs)

#     supported = [c for c in checks if c["supported"]]
#     unsupported = [c for c in checks if not c["supported"]]

#     if len(unsupported) == 0:
#         verdict = "ALL_SUPPORTED"
#         confidence = "high"
#     elif len(supported) > 0:
#         verdict = "PARTIALLY_SUPPORTED"
#         confidence = "medium"
#     else:
#         verdict = "NOT_SUPPORTED"
#         confidence = "low"

#     return {
#         "verdict": verdict,
#         "confidence": confidence,
#         "checks": checks
#     }

# BEFORE

# Only rule-based

# NOW

# Rule-based → if unsure → LLM judge

from app.rag.step4_verification.claim_extractor import extract_claims
from app.rag.step4_verification.grounding_checker import is_claim_supported
from app.rag.step4_verification.llm_verifier import llm_verify_claim

def verify_answer(answer: str, docs: list) -> dict:
    """
    Step 4 Verifier Agent:
    - Extract claims
    - Rule-based grounding check
    - LLM-based semantic verification
    - Produce a verdict
    """

    claims = extract_claims(answer)
    checks = []

    supported_count = 0

    for claim in claims:
        # 1️⃣ Fast rule-based grounding
        rule_check = is_claim_supported(claim, docs)

        # 2️⃣ LLM semantic verification (fallback)
        if not rule_check["supported"]:
            llm_check = llm_verify_claim(claim, docs)
            supported = llm_check["supported"]
            source = llm_check.get("source")
        else:
            supported = True
            source = rule_check.get("source")

        if supported:
            supported_count += 1

        checks.append({
            "claim": claim,
            "supported": supported,
            "source": source
        })

    # 3️⃣ Verdict logic
    if supported_count == len(claims):
        verdict = "ALL_SUPPORTED"
        confidence = "high"
    elif supported_count > 0:
        verdict = "PARTIALLY_SUPPORTED"
        confidence = "medium"
    else:
        verdict = "UNSUPPORTED"
        confidence = "low"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "checks": checks
    }
