from qs.cache import CacheNode, Cache
from qs.database import MemoryDatabase
from qs.utils import show_index


def test_apply_alter_change(prefilled_infra):
    (memory_db, cache), node1_idx, *_ = prefilled_infra
    show_index(memory_db.indexes[memory_db.root_index])

    cache.load(node1_idx)
    cache.alter(node1_idx, "OtherValue")
    cache.apply()
    assert memory_db.indexes[node1_idx].node.value == "OtherValue"


def test_apply_create_node(default_infra: tuple[MemoryDatabase, Cache]):
    memory_db, cache = default_infra
    show_index(memory_db.indexes[memory_db.root_index])

    cache.load(memory_db.root_index)
    cache.insert("Node2", memory_db.root_index)
    cache.apply()
    assert (
        list(memory_db.indexes[memory_db.root_index].children.values())[0].node.value
        == "Node2"
    )


def test_passthrough_cache_index(default_infra: tuple[MemoryDatabase, Cache]):
    memory_db, cache = default_infra
    show_index(memory_db.indexes[memory_db.root_index])

    cache.load(memory_db.root_index)
    cache_new_node = cache.insert("Node2", memory_db.root_index)
    cache.apply()
    assert memory_db.indexes[cache_new_node.index].node.value == "Node2"


def test_nested_node_in_cache(default_infra: tuple[MemoryDatabase, Cache]):
    memory_db, cache = default_infra
    show_index(memory_db.indexes[memory_db.root_index])

    cache.load(memory_db.root_index)
    cache_new_node = cache.insert("Node2", memory_db.root_index)
    nested_cache_node = cache.insert("Node22", cache_new_node.index)
    cache.apply()
    nested_db_node = memory_db.get_node(nested_cache_node.index)
    assert nested_db_node.value == "Node22"
    assert nested_db_node.parent == cache_new_node.index
