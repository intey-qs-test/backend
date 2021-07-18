from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    value: str
    parent: "Node"


Position = Node


class MemoryDatabase:
    def __init__(self):
        self.tree = Node(value="root", parent=None)

    def insert(self, value: str, position: Position):
        self.data[position] = value

    def delete(self, value: str, position: Position):
        if self.data.get(position):
            self.data.pop(position)

    def alter(self, new_value: str, position: Position):
        self.data[position] = new_value
