from dataclasses import dataclass
from typing import List

@dataclass
class AgentDecision:
    agent_name: str
    verdict: str   # ALLOW | BLOCK | REVIEW | REDACT
    reason: str
