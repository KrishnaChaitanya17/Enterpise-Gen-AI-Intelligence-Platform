from typing import TypedDict, List, Dict

class ModerationState(TypedDict):
    query: str
    answer: str
    agent_decisions: List[Dict]
    final_verdict: str
    redacted_answer: str
    audit_trail: List[str]
