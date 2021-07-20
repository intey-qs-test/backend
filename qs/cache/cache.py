from qs.cache.types import CacheNode, DeleteRecord, InsertRecord, UpdateRecord
from qs.database.types import Index
import typing as t

from qs.cache.errors import CacheError


class Cache:
    """
    loads database nodes and make tree of them.
    When some changes occurs, we apply them to cache
    and record changes in separate list of changes.
    This list of changes (or records) simplify applying
    changes to database: we didn't need to find difference
    Also we get opportunity to optimize actions (collapse
    opposite actions).
    Cache store nodes in `self.elements` as plain list
    unlinked nodes. When we load of create node, that has
    some parent in elements - we put this new node under
    parent, so by this we build tree.
    """

    def __init__(self, db_instance):
        self.db = db_instance
        self.elements = []
        self.unsync_changes = []

    def load(self, index: Index) -> CacheNode:
        """
        Load from database node with given index
        """
        # already loaded
        already_exists = self.find(index, include_archived=True)
        if already_exists:
            return already_exists

        node = self.db.get_node(index)

        # NOTE: for simplify logic just assert, because user has no ability
        # select unexist index. In real case, we should return None or raise
        if node is None:
            raise CacheError(f"load: Unexists node in database: {index}")

        cache_node = CacheNode.make_from_node(node)
        self._rebuild_tree(cache_node)

        return cache_node

    def insert(self, value: str, parent: Index) -> CacheNode:
        """
        Create new node and put this under parent node.
        """
        parent_node = self.find(parent)

        if not parent_node:
            raise CacheError(f"insert: not loaded or unexist {parent}")

        # NOTE: newly craete cache node has self generated index that
        # will didn't match with db index when apply this changes
        node = CacheNode(value=value, parent=parent, only_in_cache=True)
        parent_node.children[node.index] = node

        self.unsync_changes.append(
            InsertRecord(index=node.index, value=value, parent=node.parent)
        )
        return node

    def alter(self, node_index: Index, new_value: str):
        found_node = self.find(node_index)
        if found_node:
            found_node.value = new_value
            record = UpdateRecord(index=node_index, value=new_value)
            self.unsync_changes.append(record)
        else:
            raise CacheError(f"alter: not loaded or unexist {node_index}")

    def apply(self):
        for change in self.unsync_changes:
            change.apply(self.db)
        for change in self.unsync_changes:
            node = self.find(change.index, include_archived=True)
            if node:
                node.only_in_cache = False

        self.unsync_changes = []

    def delete(self, node_index: Index):
        node = self.find(node_index)
        if node:
            self.__archive(node)
            # also, we may write one by one changes for each arhived node
            # but for current realization of database - it's not needed
            self.unsync_changes.append(DeleteRecord(index=node_index))

    def __archive(self, node: CacheNode):
        node.archive = True
        for child in node.children.values():
            self.__archive(child)

    def _rebuild_tree(self, loaded_node: CacheNode):
        # when cache is empty, we can't make any links
        if not self.elements:
            self.elements.append(loaded_node)
            return

        # First step - search elements that is child for
        # loaded_node and move then under this node
        parent_node = self.find(loaded_node.parent, include_archived=True)
        if parent_node:
            parent_node.children[loaded_node.index] = loaded_node
            if parent_node.archive:
                self.__archive(parent_node)
        # No links. just put in element
        else:
            self.elements.append(loaded_node)

        # move childs under new parent if someone
        for element in self.elements:
            if element.parent == loaded_node.index:
                loaded_node.children[element.index] = element
                # archive childs when load archived
                if loaded_node.archive:
                    self.__archive(element)
                self.elements.remove(element)

    def find(self, node_index: Index, include_archived=False) -> t.Optional[CacheNode]:
        for element in self.elements:
            # exclude archive from search
            if include_archived or not element.archive:

                if element.index == node_index:
                    return element

                found_node_in_children = element.find(node_index, include_archived)
                if found_node_in_children:
                    return found_node_in_children
        return None

    def __repr__(self):
        return f"<Cache: {self.elements=}>"
