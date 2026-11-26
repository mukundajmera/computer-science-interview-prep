from __future__ import annotations

from typing import Optional


class Solution:
    def copyRandomList(self, head: Optional[Node]) -> Optional[Node]:
        if head is None:
            return None

        current = head
        while current is not None:
            clone = Node(current.val)
            clone.next = current.next
            current.next = clone
            current = clone.next

        current = head
        while current is not None:
            clone = current.next
            clone.random = current.random.next if current.random is not None else None
            current = clone.next

        copied_head = head.next
        current = head
        while current is not None:
            clone = current.next
            current.next = clone.next
            clone.next = clone.next.next if clone.next is not None else None
            current = current.next

        return copied_head
