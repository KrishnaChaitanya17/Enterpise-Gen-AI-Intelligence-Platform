def enrich_decision_with_graph(evidence, graph_engine):

    related_entities = []

    for entity in graph_engine.entities:
        if entity.lower() in str(evidence.metadata).lower():
            related_entities.append(entity)

    risk_boost = 0.0

    # Example: if critical entity involved, increase risk
    for entity in related_entities:
        if "Policy" in entity:
            risk_boost += 0.1

    enriched = {
        "graph_entities": related_entities,
        "risk_adjustment": risk_boost,
        "new_risk_score": min(evidence.risk_score + risk_boost, 1.0)
    }

    return enriched
