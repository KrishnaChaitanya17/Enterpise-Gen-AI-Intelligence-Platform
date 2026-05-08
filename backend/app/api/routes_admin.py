from fastapi import APIRouter, Depends
from app.core.role_checker import require_role
from app.ai.ingestion.job_manager import create_ingestion_job, get_job_status
from app.ai.agents.langgraph.graph_builder import run_agent_graph
from app.ai.observability.trace_store import trace_store
from app.ai.evaluation.metrics import load_evaluation_logs
from app.ai.observability.cost_tracker import check_alerts

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(admin=Depends(require_role("ADMIN"))):
    return {"message": "Admin access granted"}


# ---------------- INGESTION ----------------

@router.post("/ingest")
async def ingest(folder_path: str):
    job_id = create_ingestion_job(folder_path)
    return {"message": "Ingestion started", "job_id": job_id}


@router.get("/ingest/status/{job_id}")
async def ingest_status(job_id: str):
    return get_job_status(job_id)


# ---------------- ANALYTICS ----------------

@router.get("/analytics/usage")
def usage_analytics():
    return {
        "total_requests": len(trace_store)
    }


@router.get("/analytics/errors")
def error_analytics():
    failures = [
        t for t in trace_store
        if t.get("enterprise", {}).get("decision") == "SYSTEM_ERROR"
    ]

    return {
        "total_errors": len(failures),
        "error_rate": len(failures) / len(trace_store) if trace_store else 0
    }


@router.get("/analytics/trust")
def trust_analytics():
    logs = load_evaluation_logs()

    if not logs:
        return {"avg_trust": 0}

    avg_trust = sum(l.get("quality_score", 0) for l in logs) / len(logs)

    return {
        "avg_trust": round(avg_trust, 3),
        "total_records": len(logs)
    }


# ---------------- DEBUG ----------------

@router.post("/test-agent")
async def test_agent(query: str):
    result = await run_agent_graph(query)

    return {
        "query": query,
        "steps": result.get("steps"),
        "final_answer": result.get("answer")   # ✅ FIXED
    }

@router.get("/alerts")
def system_alerts():
    return {
        "alerts": check_alerts()
    }