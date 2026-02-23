from app.db.mongodb import db
from datetime import datetime


class PersistenceService:

    def _serialize(self, obj):
        """Recursively convert custom objects to dict for MongoDB"""
        
        # Pydantic v2
        if hasattr(obj, "model_dump"):
            return obj.model_dump()

        # Pydantic v1
        if hasattr(obj, "dict"):
            return obj.dict()

        # Generic class instance
        if hasattr(obj, "__dict__"):
            return {
                key: self._serialize(value)
                for key, value in obj.__dict__.items()
            }

        # Dict
        if isinstance(obj, dict):
            return {key: self._serialize(value) for key, value in obj.items()}

        # List
        if isinstance(obj, list):
            return [self._serialize(item) for item in obj]

        # Keep datetime as-is (Mongo supports it)
        return obj

    async def save_interaction(self, data: dict):

        document = self._serialize(data)

        document["timestamp"] = datetime.utcnow()
        document["user_id"] = document.get("user_id", "anonymous")

        await db.interactions.insert_one(document)

# This is called:

# Object Serialization Layer

# In production systems:

# You NEVER store raw domain objects

# You convert to JSON-safe dict

# You separate domain model from persistence model