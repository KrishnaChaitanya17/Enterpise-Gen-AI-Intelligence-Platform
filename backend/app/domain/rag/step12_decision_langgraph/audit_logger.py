import json
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent / "audit_logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "decision_audit.jsonl"


def log_decision(state: dict):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "decision": state.get("final_decision"),
        "execution_status": state.get("execution_status"),
        "audit_trail": state.get("audit_trail"),
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
