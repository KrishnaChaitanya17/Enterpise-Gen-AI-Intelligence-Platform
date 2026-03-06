from app.ai.observability.trace_store import trace_store


def get_metrics():

    traces = trace_store  # this is the list storing traces

    if not traces:
        return {
            "total_queries": 0,
            "avg_latency": 0,
            "avg_trust_score": 0,
            "moderation_blocks": 0
        }

    total = len(traces)

    avg_latency = sum(t.latency for t in traces) / total

    avg_trust = sum(
        t.enterprise.get("trust_score", 0) for t in traces
    ) / total

    moderation_blocks = sum(
        1 for t in traces
        if t.moderation.get("final_verdict") == "BLOCK"
    )

    return {
        "total_queries": total,
        "avg_latency": round(avg_latency, 3),
        "avg_trust_score": round(avg_trust, 3),
        "moderation_blocks": moderation_blocks
    }