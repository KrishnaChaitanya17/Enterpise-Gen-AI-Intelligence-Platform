from app.ai.evaluation.feedback_store import store_human_feedback

store_human_feedback(
    query="What is the on-call response time during an outage?",
    rating="up",
    comment="Answer is correct and clearly grounded"
)
