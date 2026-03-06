from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.auth_services import auth_service
from app.core.security import get_current_user
from fastapi import Depends

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    organization_name: Optional[str] = None
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(request: RegisterRequest):
    return await auth_service.register_org_and_admin(
        org_name = request.organization_name,
        email = request.email,
        password = request.password,
    )


@router.post("/login")
async def login(request: LoginRequest):
    return await auth_service.login(
        request.email,
        request.password,
    )

@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return current_user