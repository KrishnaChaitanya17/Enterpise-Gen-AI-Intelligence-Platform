from fastapi import APIRouter
from app.core.circuit_breaker import llm_breaker
from app.ai.observability.trace_store import trace_store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ai-health")
def ai_health():

    total_calls = len(trace_store)

    failures = sum(
        1 for t in trace_store
        if t.get("enterprise", {}).get("decision") == "SYSTEM_ERROR"
    )

    failure_rate = (failures / total_calls) if total_calls else 0

    # 🔥 Model-level stats
    model_usage = {}
    latencies = []

    for t in trace_store:
        model = t.get("model", "unknown")
        latency = t.get("latency", 0)

        latencies.append(latency)

        if model not in model_usage:
            model_usage[model] = {
                "calls": 0,
                "failures": 0
            }

        model_usage[model]["calls"] += 1

        if t.get("enterprise", {}).get("decision") == "SYSTEM_ERROR":
            model_usage[model]["failures"] += 1

    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    return {
        "status": "healthy" if failure_rate < 0.2 else "degraded",
        "total_requests": total_calls,
        "failures": failures,
        "failure_rate": round(failure_rate, 3),
        "avg_latency": round(avg_latency, 2),

        # 🔥 NEW
        "models": model_usage,

        "circuit_breaker": {
            "state": str(llm_breaker.current_state),
        }
    }