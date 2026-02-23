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
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[dict]:

        query = {}

        if user_id:
            query["user_id"] = user_id

        if status:
            query["enterprise.execution_status"] = status

        cursor = (
            db.interactions
            .find(query)
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def count(self, query: dict):
        return await db.interactions.count_documents(query)


interaction_repository = InteractionRepository()


# Because:

# API layer shouldn’t touch DB directly

# Makes unit testing easy

# Scalable architecture

# Enterprise standard pattern