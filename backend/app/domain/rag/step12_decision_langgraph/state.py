from typing import TypedDict, Dict, List


class DecisionState(TypedDict):
    evidence: Dict
    final_decision: Dict
    execution_status: str
    audit_trail: List[str]
