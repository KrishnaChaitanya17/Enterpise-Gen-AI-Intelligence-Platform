from fastapi import APIRouter
from app.core.circuit_breaker import llm_breaker
from app.ai.observability.trace_store import trace_store

router = APIRouter()


@router.get("/ai-health")
def ai_health():

    total_calls = len(trace_store)

    failures = sum(
        1 for t in trace_store
        if t.enterprise.get("decision") == "SYSTEM_ERROR"
    )

    failure_rate = (failures / total_calls) if total_calls else 0

    return {
        "status": "healthy" if failure_rate < 0.2 else "degraded",
        "total_requests": total_calls,
        "failures": failures,
        "failure_rate": round(failure_rate, 3),
        "circuit_breaker": {
            "state": str(llm_breaker.current_state),
        }
    }