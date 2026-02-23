from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EvaluationResult:
    query: str
    answer: str
    confidence: str
    verdict: str
    groundedness_score: float
    retrieval_doc_count: int
    regenerated: bool
    timestamp: datetime

@dataclass
class HumanFeedback:
    query: str
    rating: str  # "up" or "down"
    comment: Optional[str]
    timestamp: datetime