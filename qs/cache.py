from abc import ABC, abstractmethod
from enum import Enum
from qs.database import Node, Index
from dataclasses import dataclass, field
import typing as t


class CacheError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


@dataclass
class CacheNode(Node):
    children: dict[Index, "Node"] = field(default_factory=dict)

    def find(self, index: Index) -> "CacheNode":

        for child_index, child in self.children.items():
            if child_index == index:
                return child
            return child.find(index)

    @classmethod
    def make_from_node(cls, node: "Node") -> "CacheNode":
        return CacheNode(value=node.value, parent=node.parent, index=node.index)


@dataclass
class IChangeRecord(ABC):
    index: Index

    @abstractmethod
    def apply(self, db):
        pass


@dataclass
class DeleteRecord(IChangeRecord):
    def apply(self, db):
        db.delete(index=self.index)


@dataclass
class InsertRecord(IChangeRecord):
    value: str

    def apply(self, db):
        db.insert(value=self.value, parent=self.index)


@dataclass
class UpdateRecord(IChangeRecord):
    value: str

    def apply(self, db):
        db.alter(new_value=self.value, index=self.index)


class Cache:
    """
    loads database nodes and make tree of them.

    # How tree maked

    Firstly, we checks other elements, that they
    contained in loaded element, because each node from
    database has only parent link, no children

    In second step, we checks that loaded element has parent in
    already loaded elements.
    """

    def __init__(self, db_instance):
        self.db = db_instance
        self.elements = []
        self.unsync_changes = []

    def load(self, index: Index) -> CacheNode:
        node = self.db.get_node(index)

        # NOTE: for simplify logic just assert, because user has no ability
        # select unexist index. In real case, we should return None or raise
        if node is None:
            raise CacheError(f"load: Unexists node in database: {index}")

        cache_node = CacheNode.make_from_node(node)
        self._rebuild_tree(cache_node)

        return cache_node

    def make_node(self, value: str, parent: Index):
        parent_node = self.find(parent)

        if not parent_node:
            raise CacheError(f"make_node: not loaded {parent}")

        node = CacheNode(value=value, parent=parent)
        parent_node.children[node.index] = node

        self.unsync_changes.append(InsertRecord(index=node.index, value=value))
        return node

    def alter(self, node_index: Index, new_value: str):

        found_node = self.find(node_index)
        if found_node:
            found_node.value = new_value
            record = UpdateRecord(index=node_index, value=new_value)
            self.unsync_changes.append(record)
        else:
            raise CacheError(f"alter: not loaded {node_index}")

    def apply(self):
        for change in self.unsync_changes:
            change.apply(self.db)

        self.unsync_changes = []

    def delete(self, node_index: Index):
        node = self.find(node_index)
        if node:
            self.__archive(node)
            # also, we may write one by one changes for each arhived node
            # but for current realization of database - it's not needed
            self.unsync_changes.append(DeleteRecord(index=node_index))

    def __archive(self, node: CacheNode):
        node.archive = True
        for child in node.children:
            self.__archive(child)

    def _rebuild_tree(self, loaded_node: CacheNode):
        # when cache is empty, we can't make any links
        if not self.elements:
            self.elements.append(loaded_node)
            return

        # First step - search elements that is child for
        # loaded_node and move then under this node
        for element in self.elements:
            if element.parent == loaded_node.index:
                loaded_node.children[element.index] = element
                self.elements.remove(element)

        found_parent = self.find(loaded_node.parent)
        if found_parent is not None:
            # Second step. link with parent, if any
            found_parent.children[loaded_node.index] = loaded_node
        else:
            # No links. just put in element
            self.elements.append(loaded_node)

    def find(self, node_index: Index) -> t.Optional[CacheNode]:
        for element in self.elements:
            if element.index == node_index:
                return element
            found_node_in_children = element.find(node_index)
            if found_node_in_children:
                return found_node_in_children

    def __repr__(self):
        return f"<Cache: {self.elements=}>"
