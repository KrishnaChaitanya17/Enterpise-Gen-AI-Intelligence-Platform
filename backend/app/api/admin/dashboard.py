from fastapi import APIRouter
from app.ai.observability.metrics_service import get_metrics
from app.ai.observability.cost_tracker import COST_LOG

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ai-dashboard")
def ai_dashboard():

    metrics = get_metrics()

    total_cost = sum(record.get("cost", 0) for record in COST_LOG)

    models = list(set(record.get("model", "unknown") for record in COST_LOG))

    return {
        "queries": metrics.get("total_queries", 0),
        "avg_latency": metrics.get("avg_latency", 0),
        "avg_trust": metrics.get("avg_trust_score", 0),
        "moderation_blocks": metrics.get("moderation_blocks", 0),

        # 🔥 NEW
        "error_rate": metrics.get("error_rate", 0),

        "total_cost": total_cost,
        "models_used": models
    }