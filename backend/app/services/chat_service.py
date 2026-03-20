from typing import Optional
import uuid
from datetime import datetime

from app.services.ai_pipeline import ai_pipeline
from app.domain.repositories.interaction_repository import InteractionRepository


class ChatService:

    async def ask(self, query: str, user_id: str, organization_id: Optional[str]):

        conversation_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())

        organization_id = organization_id or None

        # ---------------------------------
        # 1️⃣ RUN PIPELINE (SAFE)
        # ---------------------------------
        try:
            result = await ai_pipeline.run(
                query=query,
                user_id=user_id,
                organization_id=organization_id
            )

            print("✅ PIPELINE RESULT:", result)

        except Exception as e:
            print("🔥 PIPELINE ERROR:", str(e))

            result = {
                "trace_id": trace_id,
                "answer": "System error occurred while generating the response.",
                "confidence": "low",
                "enterprise": None
            }

        # ---------------------------------
        # 2️⃣ SAVE INTERACTION (SAFE)  🔥 FIX
        # ---------------------------------
        interaction = {
            "trace_id": result.get("trace_id", trace_id),
            "conversation_id": conversation_id,
            "query": query,
            "answer": result.get("answer"),
            "confidence": result.get("confidence"),
            "enterprise": result.get("enterprise"),
            "user_id": user_id,
            "organization_id": organization_id,
            "created_at": datetime.utcnow()
        }

        try:
            await InteractionRepository().save(interaction)
            print("✅ Interaction saved:", interaction)

        except Exception as e:
            print("🔥 DB SAVE ERROR:", str(e))   # <-- THIS WAS MISSING

        # ---------------------------------
        # 3️⃣ ALWAYS RETURN RESPONSE
        # ---------------------------------
        return result

    # ---------------------------------
    # STREAMING (SAFE)
    # ---------------------------------
    async def stream_answer(self, query, user_id, organization_id):

        try:
            async for token in ai_pipeline.stream(
                query=query,
                user_id=user_id,
                organization_id=organization_id
            ):
                yield token

        except Exception as e:
            print("🔥 STREAM ERROR:", str(e))
            yield "Streaming failed."


chat_service = ChatService()