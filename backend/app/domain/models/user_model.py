from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserModel(BaseModel):

    id: Optional[str]
    organization_id: str
    email: str
    password_hash: str

    role: str = "DEVELOPER"

    created_at: datetime = datetime.utcnow()

class OrganizationUserModel(BaseModel):

    id: Optional[str]

    name: str

    created_at: datetime = datetime.utcnow()