# This creates persistent audit trail logs.
import json
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent / "audit_logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "moderation_audit.jsonl"


def log_audit(state: dict):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": state.get("query"),
        "answer": state.get("answer"),
        "final_verdict": state.get("final_verdict"),
        "agent_decisions": state.get("agent_decisions"),
        "audit_trail": state.get("audit_trail"),
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
