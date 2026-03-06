from app.ai.reasoning.schemas import AgentOpinion

class RiskAgent:

    def evaluate(self, evidence):
        risk_score = evidence.get("risk_score", 0.0)
        if risk_score > 0.5:
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
