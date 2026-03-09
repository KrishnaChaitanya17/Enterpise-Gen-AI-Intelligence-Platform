from fastapi import Depends, HTTPException
from app.core.security import get_current_user


def require_role(required_role: str):

    def role_dependency(user=Depends(get_current_user)):

        if user["role"] != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )

        return user

    return role_dependency