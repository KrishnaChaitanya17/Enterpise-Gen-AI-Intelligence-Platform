from app.services.ai_pipeline import ai_pipeline


class ChatService:

    async def ask(self, query: str, user: dict):
        return await ai_pipeline.run(
            query=query,
            user_id=user["user_id"]
        )


chat_service = ChatService()