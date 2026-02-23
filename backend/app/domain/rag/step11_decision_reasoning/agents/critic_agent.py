from app.rag.step11_decision_reasoning.schemas import AgentOpinion

class CriticAgent:

    def evaluate(self, evidence):
        if evidence.truth_score < 0.8:
            return AgentOpinion(
                agent_name="CriticAgent",
                recommendation="INVESTIGATE",
                confidence=0.85,
                reasoning="Truth score below ideal threshold."
            )

        return AgentOpinion(
            agent_name="CriticAgent",
            recommendation="APPROVE",
            confidence=0.7,
            reasoning="Evidence sufficiently strong."
        )
