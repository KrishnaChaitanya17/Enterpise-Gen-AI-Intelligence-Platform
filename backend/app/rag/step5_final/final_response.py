from app.rag.step4_verification.verifier_agent import verify_answer

def build_final_response(query: str, answer: str, sources: list):
    """
    Final orchestration step.
    Calls verification and builds the final response object.
    """

    # ✅ CALL STEP 4 VERIFICATION
    verification = verify_answer(answer, sources)

    verdict = verification.get("verdict")

    confidence_map = {
        "ALL_SUPPORTED": "high",
        "PARTIALLY_SUPPORTED": "medium",
        "NOT_SUPPORTED": "low"
    }

    confidence = confidence_map.get(verdict, "low")

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "verification": verification,   # 🔥 THIS WAS MISSING
        "confidence": confidence
    }
