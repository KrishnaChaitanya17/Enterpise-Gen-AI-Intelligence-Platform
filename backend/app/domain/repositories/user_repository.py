from app.db.mongodb import db
from bson import ObjectId


class UserRepository:

    async def create(self, document: dict):
        return await db.users.insert_one(document)

    async def get_by_email(self, email: str):
        return await db.users.find_one({"email": email})

    async def get_by_id(self, user_id: str):
        return await db.users.find_one({"_id": ObjectId(user_id)})


user_repository = UserRepository()