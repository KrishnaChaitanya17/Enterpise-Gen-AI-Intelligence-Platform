from app.ai.reasoning.schemas import AgentOpinion


class BusinessRuleAgent:

    def evaluate(self, evidence):

        moderation_status = evidence.get("moderation_status", "ALLOW")

        if moderation_status == "BLOCK":
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