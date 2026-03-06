from dataclasses import dataclass
from datetime import datetime

@dataclass
class AITrace:

    trace_id: str
    user_id: str

    query: str
    answer: str

    verification: dict
    moderation: dict
    evaluation: dict
    enterprise: dict

    latency: float
    timestamp: datetime