from __future__ import annotations

import heapq
from typing import List, Optional


class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        heap: list[tuple[int, int, ListNode]] = []
        sequence = 0
        for head in lists:
            if head is not None:
                heapq.heappush(heap, (head.val, sequence, head))
                sequence += 1

        dummy = ListNode(0)
        tail = dummy
        while heap:
            _, _, node = heapq.heappop(heap)
            if node.next is not None:
                heapq.heappush(heap, (node.next.val, sequence, node.next))
                sequence += 1
            node.next = None
            tail.next = node
            tail = tail.next
        return dummy.next
