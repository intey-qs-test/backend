import typing as t
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from qs.database.types import Index, Node

if t.TYPE_CHECKING:
    from qs.database.database import MemoryDatabase


@dataclass
class CacheNode(Node):
    """
    only_in_cache - node is present only in the cache
    """

    children: t.Dict[Index, "CacheNode"] = field(default_factory=dict)
    only_in_cache: bool = False

    def find(self, index: Index, include_archived=False) -> t.Optional["CacheNode"]:
        """
        Search node with index in children recursively.

        :param index: index of search node
        :param include_archived: didn't skip archived nodes
        """
        fast_get_child = self.children.get(index)

        if fast_get_child:
            if include_archived or not fast_get_child.archive:
                return fast_get_child

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
        """
        Make CacheNode from db Node
        """
        return CacheNode(value=node.value, parent=node.parent, index=node.index)


@dataclass  # type: ignore
class IChangeRecord(metaclass=ABCMeta):
    """
    Describe change that occurs with cache.
    Each change can applied to database

    index - changed node index.
    """

    index: Index

    @abstractmethod
    def apply(self, db: "MemoryDatabase"):
        """
        Apply change to database
        """
        pass


@dataclass
class DeleteRecord(IChangeRecord):
    """
    DeleteRecord describe delete action of node given index
    """

    def apply(self, db):
        db.delete(index=self.index)


@dataclass
class InsertRecord(IChangeRecord):
    """
    InsertRecord describe insert action of node
    with given index to node with index = self.parent
    """

    value: str
    parent: Index

    def apply(self, db):
        db.insert(value=self.value, parent=self.parent, new_node_index=self.index)


@dataclass
class UpdateRecord(IChangeRecord):
    """
    UpdateRecord describe update action on node
    with given index. Given value - is new value
    of node
    """

    value: str

    def apply(self, db):
        db.alter(new_value=self.value, index=self.index)
