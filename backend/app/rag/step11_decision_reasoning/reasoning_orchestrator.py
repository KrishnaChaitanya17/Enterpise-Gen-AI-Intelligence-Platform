from app.rag.step11_decision_reasoning.agents.planner_agent import PlannerAgent
from app.rag.step11_decision_reasoning.agents.risk_agent import RiskAgent
from app.rag.step11_decision_reasoning.agents.critic_agent import CriticAgent
from app.rag.step11_decision_reasoning.agents.business_rule_agent import BusinessRuleAgent
from app.rag.step11_decision_reasoning.decision_aggregator import aggregate_decisions


def run_decision_reasoning(evidence):

    agents = [
        PlannerAgent(),
        RiskAgent(),
        CriticAgent(),
        BusinessRuleAgent()
    ]

    opinions = [agent.evaluate(evidence) for agent in agents]

    return aggregate_decisions(opinions)
