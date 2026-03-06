from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.MONGODB_URI)

db = client["enterprise_ai"]

trace_collection = db["ai_traces"]

trace_store = []

def save_trace(trace):
    trace_store.append(trace)

    trace_collection.insert_one({
        "trace_id": trace.trace_id,
        "user_id": trace.user_id,
        "query": trace.query,
        "answer": trace.answer,
        "verification": trace.verification,
        "moderation": trace.moderation,
        "evaluation": trace.evaluation,
        "enterprise": trace.enterprise,
        "latency": trace.latency,
        "timestamp": trace.timestamp
    })