from __future__ import annotations

from collections import deque
from typing import Optional


class Solution:
    def cloneGraph(self, node: Optional[Node]) -> Optional[Node]:
        if node is None:
            return None

        clones: dict[Node, Node] = {node: Node(node.val)}
        queue = deque([node])
        while queue:
            current = queue.popleft()
            copied = clones[current]
            for neighbor in current.neighbors:
                if neighbor not in clones:
                    clones[neighbor] = Node(neighbor.val)
                    queue.append(neighbor)
                copied.neighbors.append(clones[neighbor])

        return clones[node]
