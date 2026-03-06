from app.ai.step8_multiagent_moderation.moderation_orchestrator import run_multiagent_moderation
from app.ai.step9_moderation_langgraph.audit_logger import log_audit


def moderation_node(state):
    result = run_multiagent_moderation(state["query"], state["answer"])

    state["agent_decisions"] = result["agent_decisions"]
    state["final_verdict"] = result["final_verdict"]
    state["audit_trail"].append(f"Multi-agent verdict: {result['final_verdict']}")

    return state


def redaction_node(state):
    redacted = state["answer"].replace("hack", "[REDACTED]")
    state["redacted_answer"] = redacted
    state["audit_trail"].append("Redaction applied")

    return state


def human_review_node(state):
    state["audit_trail"].append("Escalated to human review")
    state["final_verdict"] = "ALLOW"  # simulated approval

    return state


def finalize_node(state):
    state["audit_trail"].append("Final decision issued")

    # Persist audit record
    log_audit(state)

    return state
