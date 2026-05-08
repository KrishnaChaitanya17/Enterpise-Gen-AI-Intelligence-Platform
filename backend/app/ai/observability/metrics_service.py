from app.ai.observability.trace_store import trace_store
from app.ai.observability.cost_tracker import cost_store, get_total_tokens


def get_metrics():

    traces = trace_store

    if not traces:
        return {
            "total_queries": 0,
            "avg_latency": 0,
            "avg_trust_score": 0,
            "moderation_blocks": 0,
            "error_rate": 0,
            "total_cost": 0,
            "total_tokens": 0
        }

    total = len(traces)

    avg_latency = sum(t.get("latency", 0) for t in traces) / total

    avg_trust = sum(
        t.get("enterprise", {}).get("trust_score", 0)
        for t in traces
    ) / total

    moderation_blocks = sum(
        1 for t in traces
        if t.get("moderation", {}).get("final_verdict") == "BLOCK"
    )

    errors = sum(
        1 for t in traces
        if t.get("enterprise", {}).get("decision") == "SYSTEM_ERROR"
    )

    total_cost = sum(r.get("cost", 0) for r in cost_store)

    return {
        "total_queries": total,
        "total_tokens": get_total_tokens(),
        "avg_latency": round(avg_latency, 3),
        "avg_trust_score": round(avg_trust, 3),
        "moderation_blocks": moderation_blocks,
        "error_rate": round(errors / total, 3),
        "total_cost": round(total_cost, 4),
        "errors": errors
    }