from abc import ABCMeta, abstractmethod
from qs.database import Node, Index
from dataclasses import dataclass, field
import typing as t


class CacheError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


@dataclass
class CacheNode(Node):
    """
    only_in_cache - node is present only in the cache
    """

    children: dict[Index, "CacheNode"] = field(default_factory=dict)
    only_in_cache: bool = False

    def find(self, index: Index, include_archived=False) -> t.Optional["CacheNode"]:
        for _, child in self.children.items():
            # skip search in deleted nodes
            if include_archived or not child.archive:
                if child.index == index:
                    return child
                found = child.find(index, include_archived)
                if found:
                    return found
        return None

    @classmethod
    def make_from_node(cls, node: "Node") -> "CacheNode":
        return CacheNode(value=node.value, parent=node.parent, index=node.index)


@dataclass  # type: ignore
class IChangeRecord(metaclass=ABCMeta):
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
    parent: Index

    def apply(self, db):
        db.insert(value=self.value, parent=self.parent, new_node_index=self.index)


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
    contained in a loaded element, because each node from
    database has only parent link, no children

    In second step, we checks that the loaded element has parent in
    already loaded elements.
    """

    def __init__(self, db_instance):
        self.db = db_instance
        self.elements = []
        self.unsync_changes = []

    def load(self, index: Index) -> CacheNode:
        # already loaded
        if self.find(index, include_archived=True):
            return None

        node = self.db.get_node(index)

        # NOTE: for simplify logic just assert, because user has no ability
        # select unexist index. In real case, we should return None or raise
        if node is None:
            raise CacheError(f"load: Unexists node in database: {index}")

        cache_node = CacheNode.make_from_node(node)
        self._rebuild_tree(cache_node)

        return cache_node

    def insert(self, value: str, parent: Index) -> CacheNode:
        parent_node = self.find(parent)

        if not parent_node:
            raise CacheError(f"insert: not loaded or unexist {parent}")

        # NOTE: newly craete cache node has self generated index that
        # will didn't match with db index when apply this changes
        node = CacheNode(value=value, parent=parent, only_in_cache=True)
        parent_node.children[node.index] = node

        self.unsync_changes.append(
            InsertRecord(index=node.index, value=value, parent=node.parent)
        )
        return node

    def alter(self, node_index: Index, new_value: str):
        found_node = self.find(node_index)
        if found_node:
            found_node.value = new_value
            record = UpdateRecord(index=node_index, value=new_value)
            self.unsync_changes.append(record)
        else:
            raise CacheError(f"alter: not loaded or unexist {node_index}")

    def apply(self):
        for change in self.unsync_changes:
            change.apply(self.db)
        for change in self.unsync_changes:
            node = self.find(change.index, include_archived=True)
            if node:
                node.only_in_cache = False

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
        for child in node.children.values():
            self.__archive(child)

    def _rebuild_tree(self, loaded_node: CacheNode):
        # when cache is empty, we can't make any links
        if not self.elements:
            self.elements.append(loaded_node)
            return

        # First step - search elements that is child for
        # loaded_node and move then under this node
        parent_node = self.find(loaded_node.parent, include_archived=True)
        if parent_node:
            parent_node.children[loaded_node.index] = loaded_node
            if parent_node.archive:
                self.__archive(parent_node)
        # No links. just put in element
        else:
            self.elements.append(loaded_node)

        # move childs under new parent if someone
        for element in self.elements:
            if element.parent == loaded_node.index:
                loaded_node.children[element.index] = element
                # archive childs when load archived
                if loaded_node.archive:
                    self.__archive(element)
                self.elements.remove(element)

    def find(self, node_index: Index, include_archived=False) -> t.Optional[CacheNode]:
        for element in self.elements:
            # exclude archive from search
            if include_archived or not element.archive:

                if element.index == node_index:
                    return element

                found_node_in_children = element.find(node_index, include_archived)
                if found_node_in_children:
                    return found_node_in_children
        return None

    def __repr__(self):
        return f"<Cache: {self.elements=}>"
