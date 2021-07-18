from qs.cache import Cache
from qs.database import MemoryDatabase, Node


def test_can_load_element():
    memory_db = MemoryDatabase()
    cache = Cache(memory_db)
    cache.load("root")

    assert Node(value="root", parent=None) in cache.elements
