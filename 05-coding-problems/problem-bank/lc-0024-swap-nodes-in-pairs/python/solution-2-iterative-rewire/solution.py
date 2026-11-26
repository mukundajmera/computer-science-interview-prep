from typing import Optional


class Solution:
    def swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        previous = dummy

        while previous.next is not None and previous.next.next is not None:
            first = previous.next
            second = first.next
            after = second.next

            previous.next = second
            second.next = first
            first.next = after
            previous = first
        return dummy.next
