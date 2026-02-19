from app.rag.step11_decision_reasoning.schemas import AgentOpinion

class RiskAgent:

    def evaluate(self, evidence):
        if evidence.risk_score > 0.5:
            return AgentOpinion(
                agent_name="RiskAgent",
                recommendation="REJECT",
                confidence=0.95,
                reasoning="High computed risk score."
            )

        return AgentOpinion(
            agent_name="RiskAgent",
            recommendation="APPROVE",
            confidence=0.8,
            reasoning="Risk within acceptable threshold."
        )
