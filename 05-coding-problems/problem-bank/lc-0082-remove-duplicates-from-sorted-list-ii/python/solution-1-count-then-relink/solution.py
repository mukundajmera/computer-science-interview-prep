from collections import Counter
from typing import Optional


class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        counts = Counter()
        node = head
        while node is not None:
            counts[node.val] += 1
            node = node.next
        dummy = ListNode(0)
        tail = dummy
        node = head
        while node is not None:
            following = node.next
            if counts[node.val] == 1:
                tail.next = node
                tail = node
            node = following
        tail.next = None
        return dummy.next
