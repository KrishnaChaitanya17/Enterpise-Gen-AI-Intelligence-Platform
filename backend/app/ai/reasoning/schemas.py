from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class AgentOpinion:
    agent_name: str
    recommendation: str
    confidence: float
    reasoning: str


@dataclass
class FinalDecision:
    operational_decision: str
    strategic_decision: str
    overall_confidence: float
    explanation: str
    agent_opinions: List[Dict]
    final_answer: Optional[str]
