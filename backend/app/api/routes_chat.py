from fastapi import APIRouter, Query, HTTPException, Depends, Request

from app.services.enterprise_wrapper import EnterprisePipelineWrapper
from app.services.persistence import PersistenceService
from app.repositories.interaction_repository import interaction_repository
from app.schemas.interaction_schema import PaginatedResponse
from app.db.mongodb import db
from fastapi import Request
from app.core.limiter import limiter

router = APIRouter()

pipeline = EnterprisePipelineWrapper()
persistence = PersistenceService()

@router.post("/ask")
@limiter.limit("5/minute")
async def ask(request: Request, payload: dict):
    
    result = await pipeline.run(payload["query"])

    await persistence.save_interaction(result)

    return {
        "trace_id": result.get("trace_id"),
        "answer": result.get("answer"),
        "enterprise": result.get("enterprise"),
        "graph_enrichment": result.get("graph_enrichment")
    }



@router.get("/escalations")
async def get_escalations():
    records = await interaction_repository.get_history(
        status="ESCALATED",
        skip=0,
        limit=50,
    )
    return {"count": len(records), "data": records}


@router.get("/analytics/summary")
async def summary():
    total = await db.interactions.count_documents({})
    escalated = await db.interactions.count_documents(
        {"enterprise.execution_status": "ESCALATED"}
    )
    approved = await db.interactions.count_documents(
        {"enterprise.execution_status": "APPROVED"}
    )

    return {
        "total_interactions": total,
        "escalated": escalated,
        "approved": approved,
        "approval_rate": approved / total if total else 0
    }

@router.get("/history", response_model=PaginatedResponse)
async def get_history(
    user_id: str = None,
    status: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),

    # user=Depends(get_current_user)  
):
    skip = (page - 1) * limit

    query = {}
    if user_id:
        query["user_id"] = user_id
    if status:
        query["enterprise.execution_status"] = status

    total = await interaction_repository.count(query)

    records = await interaction_repository.get_history(
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit,
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": records,
    }


@router.get("/{trace_id}")
async def get_trace(trace_id: str):
    record = await interaction_repository.get_by_trace_id(trace_id)
    if not record:
        raise HTTPException(status_code=404, detail="Trace not found")
    return record