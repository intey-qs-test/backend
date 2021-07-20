from dataclasses import dataclass, field

from qs.database.utils import new_index

Index = str


@dataclass
class Node:
    value: str
    parent: str
    index: Index = field(default_factory=new_index)
    archive: bool = False


@dataclass
class IndexItem:
    node: Node
    children: dict[str, "IndexItem"] = field(default_factory=dict)

    @property
    def value(self):
        return self.node.value

    @property
    def index(self):
        return self.node.index

    @property
    def archive(self):
        return self.node.archive
