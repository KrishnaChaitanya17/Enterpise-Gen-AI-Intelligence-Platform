from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class InteractionResponse(BaseModel):
    trace_id: str
    user_id: str
    query: str
    answer: str
    enterprise: Optional[Any]
    timestamp: datetime


class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[InteractionResponse]
