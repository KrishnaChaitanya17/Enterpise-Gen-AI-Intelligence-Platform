from collections import Counter

def aggregate_votes(agent_decisions):
    verdicts = [d.verdict for d in agent_decisions]
    counts = Counter(verdicts)

    # Priority order
    if counts.get("BLOCK", 0) > 0:
        return "BLOCK"

    if counts.get("REVIEW", 0) > 0:
        return "REVIEW"

    if counts.get("REDACT", 0) > 0:
        return "REDACT"

    return "ALLOW"
