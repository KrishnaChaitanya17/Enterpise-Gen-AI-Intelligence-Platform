from app.ai.verification.claim_extractor import extract_claims
from app.ai.verification.grounding_checker import is_claim_supported
from app.ai.verification.llm_verifier import llm_verify_claim


async def verify_answer(query: str, answer: str, docs: list) -> dict:

    claims = extract_claims(answer)

    # -----------------------------
    # 📦 EMPTY DOC HANDLING
    # -----------------------------
    if not docs:
        return {
            "verdict": "NO_CONTEXT",
            "confidence": 0.4,
            "groundedness": 0.0,
            "truth_score": 0.0,
            "checks": [],
            "total_claims": 0,
            "avg_score": 0.0
        }

    # -----------------------------
    # 🧾 NO CLAIMS
    # -----------------------------
    if not claims:
        return {
            "verdict": "UNSUPPORTED",
            "confidence": 0.3,
            "groundedness": 0.0,
            "truth_score": 0.0,
            "checks": [],
            "total_claims": 0,
            "avg_score": 0.0
        }

    checks = []
    total_score = 0

    # -----------------------------
    # 🔍 VERIFY CLAIMS
    # -----------------------------
    for claim in claims:

        # 🔹 RULE-BASED
        rule_check = is_claim_supported(claim, docs)

        score = rule_check.get("score", 0.0)
        supported = score > 0
        method = rule_check.get("method")
        source = rule_check.get("source")

        # 🔹 LLM FALLBACK (only if weak grounding)
        if score < 0.3:
            llm_check = await llm_verify_claim(claim, docs)

            if llm_check.get("supported"):
                score = max(score, 0.6)
                supported = True
                method = "hybrid_llm"
                source = llm_check.get("source")

        total_score += score

        checks.append({
            "claim": claim,
            "score": score,
            "supported": supported,
            "method": method,
            "source": source
        })

    # -----------------------------
    # 📊 AGGREGATION
    # -----------------------------
    total_claims = len(claims)

    groundedness = total_score / total_claims if total_claims > 0 else 0

    truth_score = (groundedness * 0.7) + (total_claims / 10 * 0.3)
    truth_score = min(truth_score, 1.0)

    # -----------------------------
    # 🧠 VERDICT
    # -----------------------------
    if groundedness >= 0.85:
        verdict = "SUPPORTED"
        confidence = 0.9

    elif groundedness >= 0.5:
        verdict = "PARTIAL"
        confidence = 0.7

    elif groundedness >= 0.2:
        verdict = "WEAK_SUPPORT"
        confidence = 0.5

    else:
        verdict = "LIKELY_HALLUCINATION"
        confidence = 0.2

    # -----------------------------
    # 📦 FINAL OUTPUT
    # -----------------------------
    return {
        "verdict": verdict,
        "confidence": confidence,
        "groundedness": round(groundedness, 3),
        "truth_score": round(truth_score, 3),
        "checks": checks,
        "total_claims": total_claims,
        "avg_score": round(groundedness, 3)
    }