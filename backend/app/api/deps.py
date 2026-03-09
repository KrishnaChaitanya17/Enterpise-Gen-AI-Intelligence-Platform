from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from app.core.security import decode_token
from app.domain.repositories.user_repository import user_repository

security = HTTPBearer()


async def get_current_user(credentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = decode_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await user_repository.get_by_id(payload["user_id"])

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user