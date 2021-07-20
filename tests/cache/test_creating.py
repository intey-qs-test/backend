import pytest
from qs.cache.errors import CacheError


def test_create_cant_create_node_on_unloaded(default_infra):
    db, cache = default_infra

    # can't make node in unloaded element
    with pytest.raises(CacheError):
        cache.insert(value="some_value", parent=db.root_index)


def test_create_create_node(default_infra):
    db, cache = default_infra
    cache.load(db.root_index)

    created_node = cache.insert(value="some_value", parent=db.root_index)

    assert cache.elements[0].children[created_node.index].value == "some_value"


def test_create_with_nesting(default_infra):
    db, cache = default_infra
    cache.load(db.root_index)
    created_node = cache.insert(value="some_value", parent=db.root_index)
    nested_node = cache.insert(value="nested", parent=created_node.index)

    assert (
        cache.elements[0].children[created_node.index].children[nested_node.index].value
        == "nested"
    )


def test__create_in_deleted_node(default_infra):
    db, cache = default_infra
    cache.load(db.root_index)
    cache.delete(db.root_index)
    with pytest.raises(CacheError):
        cache.insert(value="some_value", parent=db.root_index)

    assert cache.elements[0].children == {}
