from fastapi import APIRouter
from app.ai.observability.cost_tracker import COST_LOG
from app.ai.observability.trace_store import TRACE_STORE

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/cost")
def get_cost():

    total_cost = sum(r["cost"] for r in COST_LOG)

    return {
        "total_queries": len(COST_LOG),
        "total_cost": round(total_cost, 6),
        "records": COST_LOG[-20:]
    }


@router.get("/latency")
def get_latency():

    latencies = [t.latency for t in TRACE_STORE]

    if not latencies:
        return {"avg_latency": 0}

    return {
        "avg_latency": sum(latencies) / len(latencies),
        "max_latency": max(latencies),
        "min_latency": min(latencies)
    }


@router.get("/trust")
def get_trust_scores():

    scores = [t.enterprise["trust_score"] for t in TRACE_STORE]

    if not scores:
        return {"avg_trust": 0}

    return {
        "avg_trust": sum(scores) / len(scores),
        "max_trust": max(scores),
        "min_trust": min(scores)
    }