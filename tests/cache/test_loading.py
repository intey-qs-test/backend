from qs.database.database import MemoryDatabase
from qs.cache.cache import Cache


def test_load_root_element(default_infra):
    memory_db, cache = default_infra

    idx = memory_db.root_index

    cache.load(idx)
    assert cache.elements
    assert idx == cache.elements[0].index


def test_load_subroot_element(prefilled_infra):
    (memory_db, cache), node1_idx, _, node2_idx, *_ = prefilled_infra

    cache.load(node1_idx)
    assert cache.elements[0].index == node1_idx
    cache.load(node2_idx)
    assert cache.elements[0].children.get(node2_idx), cache.elements[0].children
    assert cache.elements[0].children.get(node2_idx).index == node2_idx


def test_link_nodes_on_load(prefilled_infra):
    (memory_db, cache), node1_idx, node3_idx, *_ = prefilled_infra

    node1 = cache.load(node1_idx)
    assert node1 is not None

    node11 = cache.load(node3_idx)
    assert node11 is not None

    assert len(cache.elements) == 1

    assert cache.find(node3_idx) is not None, cache.elements


def test_rebuild_nodes_tree_sequence_loading(prefilled_infra):
    """
    Checks case, when element loaded in sequence and we
    can link loaded node with nested parent
    """
    (memory_db, cache), node1_idx, node11_idx, _, node111_idx, *_ = prefilled_infra

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
    (memory_db, cache), node1_idx, node11_idx, _, node111_idx, *_ = prefilled_infra

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
    (memory_db, cache), node1_idx, node11_idx, _, node111_idx, *_ = prefilled_infra

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


def test_archive_on_load__when_load_in_archived(prefilled_infra):
    (memory_db, cache), node1_idx, node11_idx, _, node111_idx, *_ = prefilled_infra

    cache.load(node111_idx)
    cache.load(node1_idx)
    cache.delete(node1_idx)
    cache.load(node11_idx)
    assert cache.find(node11_idx, include_archived=True).archive
    assert cache.find(node111_idx, include_archived=True).archive


def test_load_sibling_linking(prefilled_infra):
    (
        (memory_db, cache),
        node1_index,
        node3_index,
        node2_index,
        node4_index,
        node7_index,
        node5_index,
        node6_index,
        node8_index,
    ) = prefilled_infra
    cache.load(node1_index)
    cache.load(node3_index)
    cache.load(node4_index)
    cache.load(node7_index)
    cache.load(node5_index)
    cache.load(node8_index)
    cache.load(node6_index)
    assert len(cache.elements) == 1


def test_archive_on_load_when_load_in_archived_case_1_347_586(prefilled_infra):
    (
        (memory_db, cache),
        node1_index,
        node3_index,
        node2_index,
        node4_index,
        node7_index,
        node5_index,
        node6_index,
        node8_index,
    ) = prefilled_infra

    cache.load(node1_index)
    cache.delete(node1_index)
    cache.load(node3_index)
    cache.load(node4_index)
    cache.load(node7_index)
    cache.load(node5_index)
    cache.load(node8_index)
    cache.load(node6_index)

    assert cache.find(node6_index, include_archived=True).archive
    assert cache.find(node8_index, include_archived=True).archive
