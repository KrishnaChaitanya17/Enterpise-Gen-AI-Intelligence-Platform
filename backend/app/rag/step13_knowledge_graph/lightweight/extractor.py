import re


def extract_entities(text):
    # crude example: capitalized words
    return re.findall(r"\b[A-Z][a-zA-Z]+\b", text)


def build_graph_from_text(text, graph_store):
    entities = extract_entities(text)

    for i in range(len(entities) - 1):
        graph_store.add_relation(
            entities[i],
            "RELATED_TO",
            entities[i + 1]
        )

    return entities
