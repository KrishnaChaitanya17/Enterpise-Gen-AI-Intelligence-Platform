from app.domain.models.organization_model import OrganizationModel
from app.domain.models.user_model import UserModel
from app.domain.repositories.organization_repository import organization_repository
from app.domain.repositories.user_repository import user_repository
from app.core.security import hash_password, verify_password, create_access_token
from typing import Optional
from fastapi import HTTPException

class AuthService:

    async def register_org_and_admin(self, org_name: Optional[str], email: str, password: str):

        org_id = None

        # If organization provided → create org
        if org_name:
            existing_org = await organization_repository.get_by_name(org_name)
            if existing_org:
                raise HTTPException(status_code=400, detail="Organization already exists")

            org_doc = OrganizationModel.build(org_name, "FREE")
            org_result = await organization_repository.create(org_doc)
            org_id = org_result.inserted_id

        # Create user
        password_hash = hash_password(password)

        role = "ADMIN" if org_id else "USER"

        user_doc = UserModel.build(
            email=email,
            password_hash=password_hash,
            role=role,
            organization_id=org_id
        )

        await user_repository.create(user_doc)

        return {"message": "User registered successfully"}

    async def login(self, email: str, password: str):

        user = await user_repository.get_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({
            "user_id": str(user["_id"]),
            "organization_id": str(user["organization_id"]),
            "role": user["role"]
        })

        return {"access_token": token}
    

auth_service = AuthService()