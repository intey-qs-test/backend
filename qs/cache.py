from qs.database import Node, Index
from dataclasses import dataclass, field
import typing as t


@dataclass
class CacheNode(Node):
    children: t.Dict[Index, Node] = field(default_factory=dict)

    def find(self, index: Index) -> "CacheNode":

        for child_index, child in self.children.items():
            if child_index == index:
                return child
            return child.find(index)

    @classmethod
    def make_from_node(cls, node: "Node") -> "CacheNode":
        return CacheNode(value=node.value, parent=node.parent, index=node.index)


class Cache:
    """
    loads database nodes and make tree of them.

    # How tree maked


    Firstly, we checks that loaded element has parent in
    already loaded elements.

    In second step, we checks other elements, that they
    contained in loaded element, because each node from
    database has only parent link, no children

    """

    def __init__(self, db_instance):
        self.db = db_instance
        self.elements = []

    def load(self, index: Index) -> CacheNode:
        node = self.db.nodes[index]
        cache_node = CacheNode.make_from_node(node)
        self._rebuild_tree(cache_node)

        return cache_node

    def _rebuild_tree(self, loaded_node: CacheNode):
        # when cache is empty, we can't make any links
        if not self.elements:
            self.elements.append(loaded_node)
            return

        ### First step. link with parent, if any

        # when we has some elements, search parent node
        # for newly loaded and links them
        found_parent = None
        for element in self.elements:
            # if "root" element is parent of newly loaded - link
            if loaded_node.parent == element.index:
                found_parent = element
                break
            else:
                # make deep search
                found_parent = element.find(loaded_node.parent)
                if found_parent is not None:
                    break

        for element in self.elements:
            if element.parent == loaded_node.index:
                loaded_node.children[element.index] = element
                self.elements.remove(element)

        # No links. just put in element
        if found_parent is not None:
            found_parent.children[loaded_node.index] = loaded_node
        else:
            self.elements.append(loaded_node)
