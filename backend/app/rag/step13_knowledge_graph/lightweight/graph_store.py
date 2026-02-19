from collections import defaultdict


class SimpleGraphStore:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_relation(self, source, relation, target):
        self.graph[source].append((relation, target))

    def get_relations(self, entity):
        return self.graph.get(entity, [])

    def display(self):
        return dict(self.graph)
