from __future__ import annotations

from typing import Optional


class Solution:
    def connect(self, root: Optional[Node]) -> Optional[Node]:
        if root is None:
            return None
        level = [root]
        while level:
            next_level = []
            previous = None
            for node in level:
                if previous is not None:
                    previous.next = node
                previous = node
                if node.left is not None:
                    next_level.append(node.left)
                if node.right is not None:
                    next_level.append(node.right)
            if previous is not None:
                previous.next = None
            level = next_level
        return root
