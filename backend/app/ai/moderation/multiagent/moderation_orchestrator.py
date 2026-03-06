from app.ai.moderation.multiagent.agents.safety_agent import SafetyAgent
from app.ai.moderation.multiagent.agents.compliance_agent import ComplianceAgent
from app.ai.moderation.multiagent.agents.data_privacy_agent import DataPrivacyAgent
from app.ai.moderation.multiagent.voting_engine import aggregate_votes

def run_multiagent_moderation(query: str, answer: str):

    agents = [
        SafetyAgent(),
        ComplianceAgent(),
        DataPrivacyAgent(),
    ]

    decisions = [agent.evaluate(query, answer) for agent in agents]

    final_verdict = aggregate_votes(decisions)

    return {
        "final_verdict": final_verdict,
        "agent_decisions": [d.__dict__ for d in decisions]
    }
