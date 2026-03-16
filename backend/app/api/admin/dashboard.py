from fastapi import APIRouter
from app.ai.observability.metrics_service import get_metrics
from app.ai.observability.cost_tracker import COST_LOG

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ai-dashboard")
def ai_dashboard():

    metrics = get_metrics()

    total_cost = sum(record["cost"] for record in COST_LOG)

    models = list(set(record["model"] for record in COST_LOG))

    return {
        "queries": metrics["total_queries"],
        "avg_latency": metrics["avg_latency"],
        "avg_trust": metrics["avg_trust_score"],
        "moderation_blocks": metrics["moderation_blocks"],
        "total_cost": total_cost,
        "models_used": models
    }