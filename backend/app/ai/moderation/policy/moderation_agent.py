# This is policy-RAG reasoning, not keyword filtering.
from app.ai.moderation.policy.policy_retriever import load_policies
from app.ai.moderation.policy.schemas import ModerationResult

def moderate(query: str, answer: str) -> ModerationResult:
    policies = load_policies()

    policy_text = "\n\n".join(
        f"[{p['name']}]\n{p['content']}" for p in policies
    )

    prompt = f"""
You are a content moderation agent.

You must decide if the answer violates policy.

Policies:
{policy_text}

User Query:
{query}

Candidate Answer:
{answer}

Return one verdict:
- ALLOW
- BLOCK
- REVIEW
- REDACT

Explain the reason and cite relevant policy files.
"""

    # 🔁 Replace this block with real LLM call later
    verdict = "ALLOW"
    reason = "Answer complies with all moderation policies."
    policy_refs = ["safety_policy.txt", "compliance_policy.txt"]

    return ModerationResult(
        verdict=verdict,
        reason=reason,
        policy_refs=policy_refs
    )
