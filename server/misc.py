from dataclasses import dataclass
from fastapi import Depends
from qs.database import IndexItem, MemoryDatabase, Index
from qs.cache import Cache, CacheNode
import typing as t
from pydantic import BaseModel


class InputModel(BaseModel):
    value: str
    index: Index


def make_database() -> MemoryDatabase:
    db = MemoryDatabase(root_name="Node1")
    node1_idx = db.root_index
    # NOTE: we can use ChangeRecord for generate fixture

    _ = db.insert(value="Node2", parent=node1_idx)
    node3 = db.insert(value="Node3", parent=node1_idx)
    _ = db.insert(value="Node4", parent=node3.index)  # type: ignore
    node5 = db.insert(value="Node5", parent=node1_idx)
    _ = db.insert(value="Node6", parent=node5.index)  # type: ignore
    return db


def present_cache(cache: Cache):
    return [__present_node(element) for element in cache.elements]


def present_db(db: MemoryDatabase):
    return [__present_node(db.indexes[db.root_index])]


def __present_node(node: t.Union[CacheNode, IndexItem]):
    result = {
        "value": node.value,
        "index": node.index,
        "children": [__present_node(child) for child in node.children.values()],
        "archive": node.archive,
    }
    # cache nodes can be only present in cache
    if isinstance(node, CacheNode):
        result["only_in_cache"] = node.only_in_cache

    return result


def present_error(message: str) -> dict:
    return {"error": message}
