"""v2-variant: Composite Tree Iterators (DFS Depth-First vs. BFS Breadth-First).

Decouples hierarchical tree data structures from traversal order algorithms
using specialized iterator implementations.
"""
from collections import deque
from typing import Deque, Iterator, List, Optional


class TreeNode:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.children: List["TreeNode"] = []

    def add_child(self, child: "TreeNode") -> "TreeNode":
        self.children.append(child)
        return self

    def dfs_iterator(self) -> Iterator["TreeNode"]:
        return DfsIterator(self)

    def bfs_iterator(self) -> Iterator["TreeNode"]:
        return BfsIterator(self)


class DfsIterator:
    """Pre-order Depth-First Search Iterator using an explicit stack."""

    def __init__(self, root: Optional[TreeNode]) -> None:
        self._stack: List[TreeNode] = [root] if root else []

    def __iter__(self) -> "DfsIterator":
        return self

    def __next__(self) -> TreeNode:
        if not self._stack:
            raise StopIteration
        current = self._stack.pop()
        # Push children in reverse order so leftmost child is evaluated next
        for child in reversed(current.children):
            self._stack.append(child)
        return current


class BfsIterator:
    """Breadth-First Level-Order Search Iterator using a queue."""

    def __init__(self, root: Optional[TreeNode]) -> None:
        self._queue: Deque[TreeNode] = deque([root]) if root else deque()

    def __iter__(self) -> "BfsIterator":
        return self

    def __next__(self) -> TreeNode:
        if not self._queue:
            raise StopIteration
        current = self._queue.popleft()
        for child in current.children:
            self._queue.append(child)
        return current
