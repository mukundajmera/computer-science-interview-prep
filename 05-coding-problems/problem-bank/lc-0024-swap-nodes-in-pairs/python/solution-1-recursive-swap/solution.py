from typing import Optional


class Solution:
    def swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if head is None or head.next is None:
            return head

        second = head.next
        remaining = second.next
        second.next = head
        head.next = self.swapPairs(remaining)
        return second
