from statistics import mean
from collections import Counter
from app.ai.reasoning.schemas import FinalDecision


def aggregate_decisions(agent_opinions, final_answer: str = ""):

    recommendations = [op.recommendation for op in agent_opinions]
    counts = Counter(recommendations)

    # Operational layer
    if counts.get("REJECT", 0) > 0:
        operational = "REJECT"
    elif counts.get("INVESTIGATE", 0) > 0:
        operational = "INVESTIGATE"
    else:
        operational = "APPROVE"

    # Strategic layer
    if operational == "REJECT":
        strategic = "HOLD_DEPLOYMENT"
    elif operational == "INVESTIGATE":
        strategic = "ESCALATE_TO_REVIEW_BOARD"
    else:
        strategic = "PROCEED"

    overall_confidence = round(mean([op.confidence for op in agent_opinions]), 2)

    explanation = " | ".join(
        [f"{op.agent_name}: {op.reasoning}" for op in agent_opinions]
    )

    # If no final answer provided, synthesize one
    if not final_answer:
        final_answer = f"Decision: {operational}. Strategic Action: {strategic}."

    return FinalDecision(
        final_answer=final_answer,
        operational_decision=operational,
        strategic_decision=strategic,
        overall_confidence=overall_confidence,
        explanation=explanation,
        agent_opinions=[op.__dict__ for op in agent_opinions]
    )