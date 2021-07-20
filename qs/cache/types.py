import typing as t
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from qs.database.types import Index, Node


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
