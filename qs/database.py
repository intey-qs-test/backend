import typing as t

from dataclasses import dataclass, field
from uuid import uuid4

Index = str


def _new_index() -> Index:
    return str(uuid4())


@dataclass
class Node:
    value: str
    parent: "Node"
    index: Index = field(default_factory=_new_index)


class MemoryDatabase:
    def __init__(self):
        root = Node(value="root", parent=None)
        self.root_index = root.index
        self.nodes = {self.root_index: root}

    def insert(self, value: str, index: Index) -> t.Optional[Index]:
        if self.nodes.get(index) is None:
            return

        new_node = Node(value=value, parent=index)
        self.nodes[new_node.index] = new_node
        return new_node.index

    def delete(self, value: str, index: Index) -> bool:
        if not self.nodes.get(index):
            return False

        self.data.pop(index)
        return True

    def alter(self, new_value: str, index: Index) -> bool:
        if not self.data.get(index):
            return False

        self.nodes[index].value = new_value
        return True
