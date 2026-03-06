from datetime import datetime
from bson import ObjectId


class UserModel:

    @staticmethod
    def build(email: str, password_hash: str, role: str, organization_id: ObjectId):
        return {
            "email": email,
            "password_hash": password_hash,
            "role": role,  # ADMIN | ANALYST | USER
            "organization_id": organization_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
        }