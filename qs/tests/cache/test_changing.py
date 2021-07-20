from qs.cache import CacheError
import pytest


def test_apply_changes_in_cache(prefilled_infra):
    (memory_db, cache), node1_idx, *_ = prefilled_infra
    node1 = cache.load(node1_idx)
    new_value = "OtherValue"
    cache.alter(node1_idx, new_value)
    assert node1.value == new_value


def test_change_deleted_node(prefilled_infra):
    (memory_db, cache), node1_idx, *_ = prefilled_infra
    node1 = cache.load(node1_idx)
    cache.delete(node1_idx)

    new_value = "OtherValue"
    with pytest.raises(CacheError):
        cache.alter(node1_idx, new_value)
    assert node1.value != "OtherValue"
