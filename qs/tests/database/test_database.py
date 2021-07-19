from qs.utils import show_index
from qs.database import MemoryDatabase, Node, Index


def test_insert_node_in_root():
    db = MemoryDatabase()
    # insert in parent
    node1 = db.insert(value="Node1", parent=db.root_index)
    assert db.indexes[db.root_index].children[node1.index].node.value == "Node1"


def test_insert_in_nested_node():
    db = MemoryDatabase()
    node1 = db.insert(value="Node1", parent=db.root_index)
    node11 = db.insert(value="Node11", parent=node1.index)

    root_node = db.indexes[db.root_index]
    node1_index_item = root_node.children[node1.index]

    assert node1_index_item.children[node11.index].node.value == "Node11"


def test_archive_children():
    db = MemoryDatabase()
    node1 = db.insert(value="Node1", parent=db.root_index)
    node11 = db.insert(value="Node11", parent=node1.index)

    db.delete(node1.index)

    assert db.get_node(node11.index).archive
