import typing as t

from dataclasses import dataclass, field
from uuid import uuid4

Index = str


def _new_index() -> Index:
    return str(uuid4())


@dataclass
class Node:
    value: str
    parent: str
    index: Index = field(default_factory=_new_index)
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


class MemoryDatabase:
    def __init__(self, root_name: str = "root"):
        root = Node(value=root_name, parent="")
        self.root_index = root.index
        # save nodes in tree. When we need node itself - get "node" key.
        # use children for archiving and search
        self.indexes = {self.root_index: IndexItem(node=root)}

    def get_node(self, index: Index):
        result = self.indexes.get(index)
        if result is not None:
            return result.node

    def insert(
        self, value: str, parent: Index, new_node_index: Index = None
    ) -> t.Optional[Node]:
        # can't insert in unexist or deleted parent
        if self.indexes.get(parent) is None or self.indexes[parent].node.archive:
            return None

        # client can set node index itself. If not - we make it
        if new_node_index is None:
            new_node_index = _new_index()
        new_node = Node(value=value, parent=parent, index=new_node_index)
        # make entry for search
        new_index_item = IndexItem(node=new_node)
        self.indexes[new_node.index] = new_index_item
        # make tree
        self.indexes[parent].children[new_node.index] = new_index_item

        return new_node

    def delete(self, index: Index):
        if not self.indexes.get(index) or self.indexes[index].node.archive:
            return
        self.__archive(self.indexes[index])

    def __archive(self, index_item: IndexItem):
        index_item.node.archive = True
        for child in index_item.children.values():
            self.__archive(child)

    def alter(self, new_value: str, index: Index) -> bool:
        if not self.indexes.get(index) or self.indexes[index].node.archive:
            return False

        self.indexes[index].node.value = new_value
        return True
