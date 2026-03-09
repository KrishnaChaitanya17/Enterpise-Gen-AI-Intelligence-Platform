from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InteractionModel(BaseModel):

    id: Optional[str]

    conversation_id: str

    organization_id: str

    user_id: str
    query: str
    response: str
    created_at: datetime = datetime.utcnow()