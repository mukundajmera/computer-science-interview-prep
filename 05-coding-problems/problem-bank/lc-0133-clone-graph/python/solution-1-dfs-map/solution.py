from __future__ import annotations

from typing import Optional


class Solution:
    def cloneGraph(self, node: Optional[Node]) -> Optional[Node]:
        clones: dict[Node, Node] = {}

        def clone(current: Optional[Node]) -> Optional[Node]:
            if current is None:
                return None
            if current in clones:
                return clones[current]
            copied = Node(current.val)
            clones[current] = copied
            copied.neighbors = [clone(neighbor) for neighbor in current.neighbors]
            return copied

        return clone(node)
