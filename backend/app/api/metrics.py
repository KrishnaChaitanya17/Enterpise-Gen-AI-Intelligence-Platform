from fastapi import APIRouter
from app.ai.observability.metrics_service import get_metrics

router = APIRouter()

@router.get("/metrics/overview")
def metrics_overview():
    return get_metrics()