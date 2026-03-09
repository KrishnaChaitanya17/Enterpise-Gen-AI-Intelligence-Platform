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

        try:

            # ✅ Run full AI pipeline
            result = await ai_pipeline.run(
                query=query,
                user_id=user_id,
                organization_id=organization_id
            )

        except Exception as e:

            result = {
                "trace_id": trace_id,
                "answer": "System error occurred while generating the response.",
                "confidence": "low",
                "enterprise": None
            }

        # ✅ Save interaction to Mongo
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

        await InteractionRepository().save(interaction)

        print("✅ Interaction saved:", interaction)

        return result


chat_service = ChatService()