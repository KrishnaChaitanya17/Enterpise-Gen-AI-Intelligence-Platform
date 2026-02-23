from app.rag.step11_decision_reasoning.schemas import AgentOpinion

class PlannerAgent:

    def evaluate(self, evidence):
        if evidence.risk_score < 0.3:
            return AgentOpinion(
                agent_name="PlannerAgent",
                recommendation="APPROVE",
                confidence=0.9,
                reasoning="Low risk and high truth score."
            )
        else:
            return AgentOpinion(
                agent_name="PlannerAgent",
                recommendation="INVESTIGATE",
                confidence=0.6,
                reasoning="Elevated risk detected."
            )
