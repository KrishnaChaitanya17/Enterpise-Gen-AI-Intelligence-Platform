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

from app.ai.verification.claim_extractor import extract_claims
from app.ai.verification.grounding_checker import is_claim_supported
from app.ai.verification.llm_verifier import llm_verify_claim


def verify_answer(query:str, answer: str, docs: list) -> dict:
    """
    Enterprise Verifier Agent (Phase 5)

    Pipeline:
    1. Extract claims from answer
    2. Rule-based grounding check
    3. LLM fallback verification
    4. Aggregate results
    5. Generate structured trust signals
    """

    # -----------------------------
    # 1️⃣ Extract Claims
    # -----------------------------
    claims = extract_claims(answer)

    # Edge case: no claims
    if not claims:
        return {
            "verdict": "UNSUPPORTED",
            "confidence": 0.3,
            "groundedness": 0.0,
            "truth_score": 0.0,
            "checks": []
        }

    checks = []
    supported_count = 0

    # -----------------------------
    # 2️⃣ Verify Each Claim
    # -----------------------------
    for claim in claims:

        # Rule-based grounding
        rule_check = is_claim_supported(claim, docs)

        if rule_check.get("supported"):
            supported = True
            source = rule_check.get("source")
            method = "rule_based"
        else:
            # LLM fallback verification
            llm_check = llm_verify_claim(claim, docs)
            supported = llm_check.get("supported", False)
            source = llm_check.get("source")
            method = "llm"

        if supported:
            supported_count += 1

        checks.append({
            "claim": claim,
            "supported": supported,
            "source": source,
            "method": method
        })

    # -----------------------------
    # 3️⃣ Aggregate Results
    # -----------------------------
    total_claims = len(claims)
    groundedness = supported_count / total_claims if total_claims > 0 else 0

    # Truth score (can later weight claims)
    truth_score = groundedness

    # -----------------------------
    # 4️⃣ Verdict Logic
    # -----------------------------

    if groundedness < 0.3:
        verdict = "LIKELY_HALLUCINATION"

    
    if groundedness == 1.0:
        verdict = "SUPPORTED"
        confidence_label = "high"
    elif groundedness > 0:
        verdict = "PARTIAL"
        confidence_label = "medium"
    else:
        verdict = "UNSUPPORTED"
        confidence_label = "low"

    # -----------------------------
    # 5️⃣ Confidence Mapping
    # -----------------------------
    confidence_map = {
        "high": 0.85,
        "medium": 0.6,
        "low": 0.3
    }

    confidence_score = confidence_map.get(confidence_label, 0.5)

    # -----------------------------
    # 6️⃣ Handle Empty Docs (Fallback)
    # -----------------------------
    if not docs or len(docs) == 0:
        return {
            "verdict": "PARTIAL",
            "confidence": 0.5,
            "groundedness": 0.5,
            "truth_score": 0.5,
            "checks": checks,
            "note": "No documents retrieved, fallback applied"
        }

    # -----------------------------
    # 7️⃣ Final Output
    # -----------------------------
    return {
        "verdict": verdict,
        "confidence": confidence_score,
        "groundedness": groundedness,
        "truth_score": truth_score,
        "checks": checks
    }