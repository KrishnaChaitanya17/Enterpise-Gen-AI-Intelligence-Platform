class Relation:
    def __init__(self, source, relation_type, target):
        self.source = source
        self.relation_type = relation_type
        self.target = target

    def __repr__(self):
        return f"{self.source} -[{self.relation_type}]-> {self.target}"
