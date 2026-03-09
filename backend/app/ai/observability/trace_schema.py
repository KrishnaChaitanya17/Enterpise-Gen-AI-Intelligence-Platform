from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AITrace:
    trace_id: str
    user_id: str
    organization_id: Optional[str]   # ✅ FIX: was missing — caused TypeError in ai_pipeline.py

    query: str
    answer: str

    verification: dict
    moderation: dict
    evaluation: dict
    enterprise: dict

    latency: float
    timestamp: datetime
