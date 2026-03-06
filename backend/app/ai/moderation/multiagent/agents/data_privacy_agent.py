from app.ai.moderation.multiagent.schemas import AgentDecision

class DataPrivacyAgent:

    def evaluate(self, query: str, answer: str) -> AgentDecision:
        text = (query + " " + answer).lower()

        if any(word in text for word in ["password", "api key", "secret"]):
            return AgentDecision(
                agent_name="DataPrivacyAgent",
                verdict="BLOCK",
                reason="Sensitive data exposure risk."
            )

        return AgentDecision(
            agent_name="DataPrivacyAgent",
            verdict="ALLOW",
            reason="No sensitive data detected."
        )
