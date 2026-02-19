from app.rag.step10_evidence_engine.aggregator import aggregate_evidence
from app.rag.step12_decision_langgraph.graph import build_decision_graph
from app.rag.step13_knowledge_graph.engine.graph_core import GraphEngine
from app.rag.step13_knowledge_graph.enterprise.reasoning_engine import (
    enrich_decision_with_graph,
)


def run_enterprise_pipeline(verification: dict, evaluation: dict, moderation: dict):

    # STEP 10 — Evidence
    evidence = aggregate_evidence(
        verification,
        evaluation,
        moderation,
    )

    # STEP 12 — Decision Workflow
    graph = build_decision_graph()

    decision_state = {
        "evidence": evidence,
        "final_decision": {},
        "execution_status": "",
        "audit_trail": [],
    }

    decision_result = graph.invoke(decision_state)

    # STEP 13 — Graph Enrichment
    graph_engine = GraphEngine()
    graph_engine.add_entity("PolicyEngine", "SYSTEM")
    graph_engine.add_entity("RiskAgent", "AGENT")
    graph_engine.add_relation("PolicyEngine", "INTERACTS_WITH", "RiskAgent")

    enrichment = enrich_decision_with_graph(
        evidence,
        graph_engine,
    )

    return {
        "evidence_bundle": evidence,
        "decision_workflow": decision_result,
        "graph_enrichment": enrichment,
    }
