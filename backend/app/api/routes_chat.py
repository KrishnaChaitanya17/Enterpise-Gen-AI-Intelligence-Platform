from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.security import get_current_user
from app.services.chat_service import chat_service
from app.domain.repositories.interaction_repository import InteractionRepository
from app.utils.mongo_utils import serialize_mongo
import inspect

print("ChatService loaded from:", inspect.getfile(chat_service.__class__))
print("ChatService.ask signature:", inspect.signature(chat_service.ask))


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str


# ------------------------------
# Ask Chat
# ------------------------------
@router.post("/ask")
async def ask_chat(
    payload: ChatRequest,
    user=Depends(get_current_user)
):

    org_id = user.get("organization_id")

    if org_id in ["None", "", None]:
        org_id = None

    response = await chat_service.ask(
        query=payload.query,
        user_id=user["user_id"],
        organization_id=org_id
    )

    return response


# ------------------------------
# Streaming Chat (Real-time)
# ------------------------------
@router.post("/stream")
async def stream_chat(
    payload: ChatRequest,
    user=Depends(get_current_user)
):

    org_id = user.get("organization_id")

    if org_id in ["None", "", None]:
        org_id = None

    async def event_generator():

        async for chunk in chat_service.stream_answer(
            query=payload.query,
            user_id=user["user_id"],
            organization_id=org_id
        ):
            yield f"data: {chunk}\n\n"

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

    history = serialize_mongo(history)

    return {
        "history": history
    }


# ------------------------------
# Conversation Details
# ------------------------------
@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user=Depends(get_current_user)
):

    convo = await InteractionRepository.get_conversation(
        conversation_id,
        user["user_id"]
    )

    if not convo:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    convo = serialize_mongo(convo)

    return {
        "conversation": convo
    }


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