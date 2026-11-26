from __future__ import annotations

from typing import List, Optional


class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        values: list[int] = []
        for head in lists:
            current = head
            while current is not None:
                values.append(current.val)
                current = current.next

        values.sort()
        dummy = ListNode(0)
        tail = dummy
        for value in values:
            tail.next = ListNode(value)
            tail = tail.next
        return dummy.next
