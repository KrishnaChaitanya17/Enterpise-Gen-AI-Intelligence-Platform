from app.rag.step8_multiagent_moderation.schemas import AgentDecision

class SafetyAgent:

    def evaluate(self, query: str, answer: str) -> AgentDecision:
        text = (query + " " + answer).lower()

        if any(word in text for word in ["hack", "exploit", "attack", "bypass"]):
            return AgentDecision(
                agent_name="SafetyAgent",
                verdict="BLOCK",
                reason="Potential harmful instruction detected."
            )

        if any(word in text for word in ["kill", "harm"]):
            return AgentDecision(
                agent_name="SafetyAgent",
                verdict="BLOCK",
                reason="Violence-related content detected."
            )

        return AgentDecision(
            agent_name="SafetyAgent",
            verdict="ALLOW",
            reason="No safety violations detected."
        )
