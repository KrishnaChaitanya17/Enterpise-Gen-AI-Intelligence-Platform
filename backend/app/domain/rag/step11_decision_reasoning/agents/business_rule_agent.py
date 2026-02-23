from app.rag.step11_decision_reasoning.schemas import AgentOpinion

class BusinessRuleAgent:

    def evaluate(self, evidence):
        if evidence.moderation_status == "BLOCK":
            return AgentOpinion(
                agent_name="BusinessRuleAgent",
                recommendation="REJECT",
                confidence=1.0,
                reasoning="Blocked by governance policy."
            )

        return AgentOpinion(
            agent_name="BusinessRuleAgent",
            recommendation="APPROVE",
            confidence=0.85,
            reasoning="Complies with governance policy."
        )
