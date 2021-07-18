from qs.database import Node


class Cache:
    def __init__(self, db_instance):
        self.db = db_instance
        self.elements = []

    def load(self, element_value: str):
        self.elements.append(Node(element_value, parent=None))
