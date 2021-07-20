from qs.database.database import MemoryDatabase


def test_insert_node_in_root(default_infra):
    db, *_ = default_infra
    # insert in parent
    node1 = db.insert(value="Node1", parent=db.root_index)
    assert db.indexes[db.root_index].children[node1.index].node.value == "Node1"


def test_insert_in_nested_node(default_infra):
    db, *_ = default_infra
    node1 = db.insert(value="Node1", parent=db.root_index)
    node11 = db.insert(value="Node11", parent=node1.index)

    root_node = db.indexes[db.root_index]
    node1_index_item = root_node.children[node1.index]

    assert node1_index_item.children[node11.index].node.value == "Node11"


def test_archive_children(default_infra):
    db, *_ = default_infra
    node1 = db.insert(value="Node1", parent=db.root_index)
    node11 = db.insert(value="Node11", parent=node1.index)

    db.delete(node1.index)

    assert db.get_node(node11.index).archive


def test_delete_archived(prefilled_infra):
    (db, _), node1_idx, *_ = prefilled_infra
    db.delete(index=node1_idx)
    db.delete(index=node1_idx)


def test_insert_in_deleted(prefilled_infra):
    (db, _), node1_idx, *_ = prefilled_infra
    db.delete(index=node1_idx)
    assert db.insert(value="some", parent=node1_idx) is None


def test_alter_deleted(prefilled_infra):
    (db, _), node1_idx, *_ = prefilled_infra
    db.delete(index=node1_idx)
    assert not db.alter(new_value="other", index=node1_idx)
