from app.ai.reasoning.agents.planner_agent import PlannerAgent
from app.ai.reasoning.agents.risk_agent import RiskAgent
from app.ai.reasoning.agents.critic_agent import CriticAgent
from app.ai.reasoning.agents.business_rule_agent import BusinessRuleAgent
from app.ai.reasoning.decision_aggregator import aggregate_decisions
from app.ai.reasoning.self_healing_rag import retry_with_reasoning


async def run_decision_reasoning(evidence):

    query = evidence.get("query")
    answer = evidence.get("answer")
    verification = evidence.get("verification", {})

    # -----------------------------
    # Multi-Agent Reasoning
    # -----------------------------
    agents = [
        PlannerAgent(),
        RiskAgent(),
        CriticAgent(),
        BusinessRuleAgent()
    ]

    opinions = [agent.evaluate(evidence) for agent in agents]

    # -----------------------------
    # Self-Healing RAG
    # -----------------------------
    final_answer = answer

    confidence = evidence.get("confidence", "low")

    should_retry = (
        not verification or
        verification.get("verdict") != "SUPPORTED" or
        confidence == "low"
    )

    if should_retry:
        final_answer = await retry_with_reasoning(
            query,
            answer,
            verification
        )

    # -----------------------------
    # Aggregate Decisions
    # -----------------------------
    decision = aggregate_decisions(opinions)

    decision.final_answer = final_answer

    print("VERIFICATION:", verification)
    print("FINAL ANSWER AFTER HEALING:", final_answer)

    return decision