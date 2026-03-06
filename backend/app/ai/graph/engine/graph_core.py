class GraphEngine:
    def __init__(self):
        self.entities = {}
        self.relations = []

    def add_entity(self, name, type="GENERIC"):
        if name not in self.entities:
            self.entities[name] = type
        return name

    def add_relation(self, source, relation_type, target):
        self.relations.append((source, relation_type, target))

    def get_neighbors(self, entity):
        return [
            (rel, tgt)
            for src, rel, tgt in self.relations
            if src == entity
        ]

    def display(self):
        return self.relations
