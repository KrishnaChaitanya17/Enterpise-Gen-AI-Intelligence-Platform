from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class EvidenceBundle:
    truth_score : float
    groundedness: float
    moderation_status: str
    risk_score: float
    confidence: str
    metadata: Dict[str, Any]