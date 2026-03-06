from dataclasses import dataclass
from typing import List

@dataclass
class ModerationResult:
    verdict: str          # ALLOW | BLOCK | REVIEW | REDACT
    reason: str
    policy_refs: List[str]