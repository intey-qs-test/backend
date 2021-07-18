import pytest
from qs.cache import Cache
from qs.database import MemoryDatabase, Node


@pytest.fixture
def prefilled_infra(default_infra):
    db = default_infra[0]

    node1_idx = db.insert("Node1", db.root_index)
    node11_idx = db.insert("Node11", node1_idx)
    node2_idx = db.insert("Node2", db.root_index)

    return default_infra, node1_idx, node11_idx, node2_idx


@pytest.fixture
def default_infra():
    db = MemoryDatabase()

    return db, Cache(db)


def test_load_root_element(default_infra):
    memory_db, cache = default_infra

    idx = memory_db.root_index

    cache.load(idx)
    assert cache.elements
    assert idx == cache.elements[0].index


def test_load_subroot_element(prefilled_infra):
    (memory_db, cache), node1_idx, node11_idx, node2_idx = prefilled_infra

    cache.load(node1_idx)
    assert cache.elements[0].index == node1_idx
    cache.load(node11_idx)
    assert cache.elements[1].index == node11_idx
