from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from app.core.security import get_current_user
from app.services.chat_service import chat_service
from app.domain.repositories.interaction_repository import InteractionRepository
from app.utils.mongo_utils import serialize_mongo


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str


# ------------------------------
# Ask Chat
# ------------------------------
@router.post("/ask")
async def ask_chat(payload: ChatRequest, user=Depends(get_current_user)):

    org_id = user.get("organization_id") or None

    return await chat_service.ask(
        query=payload.query,
        user_id=user["user_id"],
        organization_id=org_id,
    )


# ------------------------------
# Streaming Chat
# ------------------------------
@router.post("/stream")
async def stream_chat(payload: ChatRequest, user=Depends(get_current_user)):

    org_id = user.get("organization_id") or None

    async def event_generator():
        async for token in chat_service.stream_answer(
            payload.query,
            user["user_id"],
            org_id,
            payload.conversation_id
        ):
            yield f"data: {token}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


# ------------------------------
# Chat History
# ------------------------------
@router.get("/history")
async def get_history(user=Depends(get_current_user)):

    history = await InteractionRepository.get_user_history(
        user_id=user["user_id"],
        organization_id=user.get("organization_id")
    )

    return {"history": serialize_mongo(history)}


# ------------------------------
# Conversation Details
# ------------------------------
@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str, user=Depends(get_current_user)):

    convo = await InteractionRepository.get_conversation(
        conversation_id,
        user["user_id"]
    )

    if not convo:
        raise HTTPException(status_code=404, detail="Not found")

    return {"conversation": serialize_mongo(convo)}

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