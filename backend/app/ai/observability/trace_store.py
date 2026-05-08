from pymongo import MongoClient
from datetime import datetime
from app.core.config import settings

client = MongoClient(settings.MONGODB_URI)
db = client["enterprise_ai"]
trace_collection = db["ai_traces"]

# In-memory store for analytics
TRACE_STORE = []

# Alias
trace_store = TRACE_STORE


def save_trace(trace: dict):
    # Store in memory
    TRACE_STORE.append(trace)

    # Store in DB safely
    trace_collection.insert_one({
        "trace_id": trace.get("trace_id"),
        "query": trace.get("query"),
        "answer": trace.get("answer"),
        "latency": trace.get("latency"),
        "steps": trace.get("steps", []),
        "status": trace.get("status", "UNKNOWN"),
        "error": trace.get("error"),
        "enterprise": trace.get("enterprise", {}),
        "moderation": trace.get("moderation", {}),
        "timestamp": trace.get("timestamp", datetime.utcnow())
    })


def get_traces():
    return TRACE_STORE