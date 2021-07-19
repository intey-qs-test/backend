from qs.cache import Cache
from qs.database import MemoryDatabase, Node


def test_load_root_element(default_infra):
    memory_db, cache = default_infra

    idx = memory_db.root_index

    cache.load(idx)
    assert cache.elements
    assert idx == cache.elements[0].index


def test_load_subroot_element(prefilled_infra):
    (memory_db, cache), node1_idx, node11_idx, node2_idx, *_ = prefilled_infra

    cache.load(node1_idx)
    assert cache.elements[0].index == node1_idx
    cache.load(node2_idx)
    assert cache.elements[1].index == node2_idx


def test_link_nodes_on_load(prefilled_infra):
    (memory_db, cache), node1_idx, node11_idx, *_ = prefilled_infra

    node1 = cache.load(node1_idx)
    assert node1 is not None
    node11 = cache.load(node11_idx)
    assert node11 is not None

    assert node1.find(node11_idx) is not None


def test_rebuild_nodes_tree_sequence_loading(prefilled_infra):
    """
    Checks case, when element loaded in sequence and we
    can link loaded node with nested parent
    """
    (memory_db, cache), node1_idx, node11_idx, _, node111_idx = prefilled_infra

    node1 = cache.load(node1_idx)
    node11 = cache.load(node11_idx)
    node111 = cache.load(node111_idx)
    assert len(cache.elements) == 1
    cn1 = cache.elements[0]

    assert cn1.index == node1.index
    assert cn1.children[node11_idx].index == node11.index
    assert cn1.children[node11_idx].children[node111_idx].index == node111_idx


def test_rebuild_nodes_tree_sequence_loading_from_child_to_parent(prefilled_infra):
    """
    Checks case, when element loaded in sequence and we
    can link loaded node with nested parent
    """
    (memory_db, cache), node1_idx, node11_idx, _, node111_idx = prefilled_infra

    node111 = cache.load(node111_idx)
    node11 = cache.load(node11_idx)
    node1 = cache.load(node1_idx)
    assert len(cache.elements) == 1
    cn1 = cache.elements[0]

    assert cn1.index == node1.index
    assert cn1.children[node11_idx].index == node11.index
    assert cn1.children[node11_idx].children[node111_idx].index == node111_idx


def test_rebuild_nodes_tree_when_middle_node_loaded(prefilled_infra):
    """
    Checks case, when load element that has loaded parent and loaded child
    """
    (memory_db, cache), node1_idx, node11_idx, _, node111_idx = prefilled_infra

    node1 = cache.load(node1_idx)
    node111 = cache.load(node111_idx)
    assert len(cache.elements) == 2

    node11 = cache.load(node11_idx)
    assert len(cache.elements) == 1
    cn1 = cache.elements[0]

    assert cn1.index == node1.index
    assert cn1.children[node11_idx].index == node11.index
    assert cn1.children[node11_idx].children[node111_idx].index == node111_idx


def test_load_same_twice(prefilled_infra):
    (memory_db, cache), node1_idx, *_ = prefilled_infra

    cache.load(node1_idx)
    cache.load(node1_idx)
    assert len(cache.elements) == 1
