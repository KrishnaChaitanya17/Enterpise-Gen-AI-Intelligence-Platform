from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas import ChatRequest
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/ask")
async def ask_chat(
    request: ChatRequest,
    current_user=Depends(get_current_user)
):

    return await chat_service.ask(request.query, current_user)

# /chat/ask
#  → chat_service.ask()
#  → ai_pipeline.run()
#  → run_rag()
#  → verify_answer()
#  → reasoning_orchestrator()
#  → evaluator()
#  → enterprise_pipeline()
#  → moderation
#  → final response