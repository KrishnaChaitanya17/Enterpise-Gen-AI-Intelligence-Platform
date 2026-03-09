from fastapi import APIRouter, Depends
from app.core.role_checker import require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(admin=Depends(require_role("ADMIN"))):

    return {
        "message": "Admin access granted"
    }