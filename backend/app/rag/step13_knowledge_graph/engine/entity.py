class Entity:
    def __init__(self, name, type="GENERIC"):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"{self.type}:{self.name}"
