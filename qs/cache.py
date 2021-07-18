from qs.database import Node


class Cache:
    def __init__(self, db_instance):
        self.db = db_instance
        self.elements = []

    def load(self, index: str):
        node = self.db.nodes[index]
        self.elements.append(node)
