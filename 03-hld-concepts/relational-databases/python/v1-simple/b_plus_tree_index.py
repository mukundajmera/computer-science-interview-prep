import bisect
from typing import Any, List, Optional, Tuple

class Node:
    def __init__(self, is_leaf: bool = False):
        self.is_leaf = is_leaf
        self.keys: List[Any] = []

class LeafNode(Node):
    def __init__(self):
        super().__init__(is_leaf=True)
        self.values: List[Any] = []
        self.next_leaf: Optional['LeafNode'] = None

class InternalNode(Node):
    def __init__(self):
        super().__init__(is_leaf=False)
        self.children: List[Node] = []

class BPlusTreeIndex:
    def __init__(self, order: int = 4):
        self.order = max(3, order)
        self.root: Node = LeafNode()

    def insert(self, key: Any, value: Any) -> None:
        root = self.root
        if len(root.keys) == self.order - 1:
            new_root = InternalNode()
            self.root = new_root
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)

    def _split_child(self, parent: InternalNode, index: int) -> None:
        child = parent.children[index]
        if child.is_leaf:
            self._split_leaf(parent, index, child) # type: ignore
        else:
            self._split_internal(parent, index, child) # type: ignore

    def _split_leaf(self, parent: InternalNode, index: int, leaf: LeafNode) -> None:
        new_leaf = LeafNode()
        mid = self.order // 2

        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]

        new_leaf.next_leaf = leaf.next_leaf
        leaf.next_leaf = new_leaf

        parent.children.insert(index + 1, new_leaf)
        parent.keys.insert(index, new_leaf.keys[0])

    def _split_internal(self, parent: InternalNode, index: int, internal: InternalNode) -> None:
        new_internal = InternalNode()
        mid = self.order // 2

        up_key = internal.keys[mid]

        new_internal.keys = internal.keys[mid + 1:]
        new_internal.children = internal.children[mid + 1:]

        internal.keys = internal.keys[:mid]
        internal.children = internal.children[:mid + 1]

        parent.children.insert(index + 1, new_internal)
        parent.keys.insert(index, up_key)

    def _insert_non_full(self, node: Node, key: Any, value: Any) -> None:
        if node.is_leaf:
            idx = bisect.bisect_left(node.keys, key)
            if idx < len(node.keys) and node.keys[idx] == key:
                node.values[idx] = value # type: ignore
            else:
                node.keys.insert(idx, key)
                node.values.insert(idx, value) # type: ignore
        else:
            idx = bisect.bisect_right(node.keys, key)
            child = node.children[idx] # type: ignore
            if len(child.keys) == self.order - 1:
                self._split_child(node, idx) # type: ignore
                if key >= node.keys[idx]:
                    idx += 1
            self._insert_non_full(node.children[idx], key, value) # type: ignore

    def search(self, key: Any) -> Optional[Any]:
        leaf = self._find_leaf(self.root, key)
        idx = bisect.bisect_left(leaf.keys, key)
        if idx < len(leaf.keys) and leaf.keys[idx] == key:
            return leaf.values[idx]
        return None

    def range_scan(self, start_key: Any, end_key: Any) -> List[Tuple[Any, Any]]:
        leaf = self._find_leaf(self.root, start_key)
        results = []
        while leaf:
            for i, k in enumerate(leaf.keys):
                if start_key <= k <= end_key:
                    results.append((k, leaf.values[i]))
                elif k > end_key:
                    return results
            leaf = leaf.next_leaf
        return results

    def _find_leaf(self, node: Node, key: Any) -> LeafNode:
        while not node.is_leaf:
            idx = bisect.bisect_right(node.keys, key)
            node = node.children[idx] # type: ignore
        return node # type: ignore
