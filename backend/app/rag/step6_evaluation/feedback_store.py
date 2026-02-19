import json
from pathlib import Path
from dataclasses import asdict
from datetime import datetime
from .schemas import HumanFeedback

STORE_PATH = Path(__file__).parent

def save_evaluation(result):
    file_path = STORE_PATH / "evaluation_results.jsonl"
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(result), default=str) + "\n")


FEEDBACK_LOG = STORE_PATH / "human_feedback.jsonl"

def store_human_feedback(query: str, rating: str, comment: str = None):
    feedback = HumanFeedback(
        query=query,
        rating=rating,
        comment=comment,
        timestamp=datetime.utcnow()
    )

    with open(FEEDBACK_LOG, "a") as f:
        f.write(json.dumps(feedback.__dict__, default=str) + "\n")
