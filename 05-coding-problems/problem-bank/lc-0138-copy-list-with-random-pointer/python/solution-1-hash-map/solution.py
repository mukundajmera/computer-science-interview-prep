from __future__ import annotations

from typing import Optional


class Solution:
    def copyRandomList(self, head: Optional[Node]) -> Optional[Node]:
        if head is None:
            return None

        clones: dict[Node, Node] = {}
        current = head
        while current is not None:
            clones[current] = Node(current.val)
            current = current.next

        current = head
        while current is not None:
            clone = clones[current]
            clone.next = clones.get(current.next)
            clone.random = clones.get(current.random)
            current = current.next

        return clones[head]
