import pytest
from qs.database.database import MemoryDatabase
from qs.cache.cache import Cache


@pytest.fixture
def default_infra():
    db = MemoryDatabase()

    return db, Cache(db)


@pytest.fixture
def prefilled_infra(default_infra):
    db: MemoryDatabase = default_infra[0]
    """
    +- node1
       +- node2
       +- node3
       |  +- node4
       |     +- node7
       +- node5
          +- node6
             +- node8
    """

    node1 = db.indexes[db.root_index]
    node2 = db.insert(value="Node2", parent=node1.index)
    node3 = db.insert(value="Node3", parent=node1.index)
    node4 = db.insert(value="Node4", parent=node3.index)  # type: ignore
    node7 = db.insert(value="Node7", parent=node4.index)  # type: ignore
    node5 = db.insert(value="Node5", parent=node1.index)
    node6 = db.insert(value="Node6", parent=node5.index)  # type: ignore
    node8 = db.insert(value="Node8", parent=node6.index)  # type: ignore

    return (
        default_infra,
        node1.index,
        node3.index,
        node2.index,
        node4.index,
        node7.index,
        node5.index,
        node6.index,
        node8.index,
    )
