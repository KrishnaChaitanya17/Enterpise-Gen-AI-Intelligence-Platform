from app.ai.moderation.multiagent.schemas import AgentDecision

class ComplianceAgent:

    def evaluate(self, query: str, answer: str) -> AgentDecision:
        text = (query + " " + answer).lower()

        if "legal advice" in text or "medical advice" in text:
            return AgentDecision(
                agent_name="ComplianceAgent",
                verdict="REVIEW",
                reason="Possible regulated advice content."
            )

        return AgentDecision(
            agent_name="ComplianceAgent",
            verdict="ALLOW",
            reason="No compliance violations."
        )
