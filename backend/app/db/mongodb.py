# from motor.motor_asyncio import AsyncIOMotorClient
# import os

# class MongoDB:

#     def __init__(self):
#         self.client = AsyncIOMotorClient(
#             os.getenv("MONGO_URI", "mongodb://localhost:27017")
#         )
#         self.database = self.client["enterprise_genai"]

#     def get_db(self):
#         return self.database


# mongo = MongoDB()
# db = mongo.get_db()

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client["enterprise_ai_platform"]