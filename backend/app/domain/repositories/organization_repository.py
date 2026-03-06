from app.db.mongodb import db
from bson import ObjectId


class OrganizationRepository:

    async def create(self, document: dict):
        return await db.organizations.insert_one(document)

    async def get_by_id(self, org_id: str):
        return await db.organizations.find_one({"_id": ObjectId(org_id)})

    async def get_by_name(self, name: str):
        return await db.organizations.find_one({"name": name})


organization_repository = OrganizationRepository()