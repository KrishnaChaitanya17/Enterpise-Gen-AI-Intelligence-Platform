from fastapi import APIRouter, Depends
from app.core.role_checker import require_role
from app.ai.ingestion.job_manager import create_ingestion_job, get_job_status
from app.ai.agents.langgraph.graph_builder import run_agent_graph

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(admin=Depends(require_role("ADMIN"))):

    return {
        "message": "Admin access granted"
    }

@router.post("/admin/ingest")
async def ingest(folder_path: str):

    job_id = create_ingestion_job(folder_path)

    return {
        "message": "Ingestion started",
        "job_id": job_id
    }


@router.get("/admin/ingest/status/{job_id}")
async def ingest_status(job_id: str):

    return get_job_status(job_id)

@router.post("/test-agent")
async def test_agent(query: str):
    result = await run_agent_graph(query)
    return {
        "query": query,
        "route": result.get("route"),
        "steps": result.get("steps"),
        "final_answer": result.get("final_answer")
    }