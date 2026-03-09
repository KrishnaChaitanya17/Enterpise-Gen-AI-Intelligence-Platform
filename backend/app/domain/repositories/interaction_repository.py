from app.db.mongodb import db
from typing import Optional, List
from datetime import datetime


class InteractionRepository:

    async def save(self, document: dict):
        return await db.interactions.insert_one(document)

    async def get_by_trace_id(self, trace_id: str):
        return await db.interactions.find_one({"trace_id": trace_id})

    async def get_history(
        self,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[dict]:

        query = {}

        if user_id:
            query["user_id"] = user_id

        cursor = (
            db.interactions
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    # ✅ used by /chat/history
    @staticmethod
    async def get_user_history(user_id: str, organization_id: Optional[str]):

        query = {
            "user_id": user_id
        }

        # only filter if valid org_id exists
        if organization_id and organization_id != "None":
            query["organization_id"] = organization_id

        cursor = db.interactions.find(query).sort("created_at", -1)

        print("History query:", query)

        return [doc async for doc in cursor]

    # ✅ used by conversation view
    @staticmethod
    async def get_conversation(conversation_id: str, user_id: str):

        cursor = db.interactions.find(
            {
                "conversation_id": conversation_id,
                "user_id": user_id
            }
        ).sort("created_at", 1)

        return [doc async for doc in cursor]


interaction_repository = InteractionRepository()