from app.ai.reasoning.reasoning_orchestrator import run_decision_reasoning
from app.ai.reasoning.decision_flow.audit_logger import log_decision


def reasoning_node(state):
    decision = run_decision_reasoning(state["evidence"])

    state["final_decision"] = decision.__dict__
    state["audit_trail"].append("Decision reasoning completed")

    return state


def execution_node(state):
    state["execution_status"] = "EXECUTED"
    state["audit_trail"].append("Decision executed")

    return state


def escalation_node(state):
    state["execution_status"] = "ESCALATED"
    state["audit_trail"].append("Decision escalated to review board")

    return state


def rejection_node(state):
    state["execution_status"] = "BLOCKED"
    state["audit_trail"].append("Decision blocked due to rejection")

    return state


def finalize_node(state):
    state["audit_trail"].append("Finalized decision workflow")

    log_decision(state)

    return state
