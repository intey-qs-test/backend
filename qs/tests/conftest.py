import pytest
from qs.database import MemoryDatabase
from qs.cache import Cache


@pytest.fixture
def default_infra():
    db = MemoryDatabase()

    return db, Cache(db)


@pytest.fixture
def prefilled_infra(default_infra):
    db = default_infra[0]

    #             root
    #            /    \
    #         node1  node2
    #         /
    #       node11
    #       /
    #   node111
    node1 = db.insert("Node1", db.root_index)
    node11 = db.insert("Node11", node1.index)
    node2 = db.insert("Node2", db.root_index)
    node111 = db.insert("Node111", node11.index)

    return default_infra, node1.index, node11.index, node2.index, node111.index
