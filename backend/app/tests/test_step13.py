from app.rag.step13_knowledge_graph.lightweight.graph_store import SimpleGraphStore
from app.rag.step13_knowledge_graph.lightweight.extractor import build_graph_from_text

from app.rag.step13_knowledge_graph.engine.graph_core import GraphEngine
from app.rag.step13_knowledge_graph.enterprise.graph_queries import find_paths


text = "PolicyEngine interacts with RiskAgent and ComplianceAgent."

# A — Lightweight
graph_store = SimpleGraphStore()
build_graph_from_text(text, graph_store)

print("Lightweight Graph:")
print(graph_store.display())


# B — Engine
engine = GraphEngine()
engine.add_entity("PolicyEngine", "SYSTEM")
engine.add_entity("RiskAgent", "AGENT")
engine.add_relation("PolicyEngine", "INTERACTS_WITH", "RiskAgent")

print("\nEngine Graph:")
print(engine.display())


# C — Multi-hop query
paths = find_paths(engine, "PolicyEngine")

print("\nEnterprise Graph Paths:")
print(paths)
