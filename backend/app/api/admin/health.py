from fastapi import APIRouter
import psutil
import time

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ai-health")
def ai_health():

    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    return {
        "status": "healthy",
        "cpu_usage": cpu,
        "memory_usage": memory,
        "timestamp": time.time()
    }