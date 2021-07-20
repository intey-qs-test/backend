import typing as t

from qs.database.types import Index, Node, IndexItem
from qs.database.utils import new_index


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
            new_node_index = new_index()
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
