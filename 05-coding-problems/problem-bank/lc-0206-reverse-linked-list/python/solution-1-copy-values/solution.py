from typing import List, Optional


class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        values: List[int] = []
        while head is not None:
            values.append(head.val)
            head = head.next

        dummy = ListNode(0)
        tail = dummy
        for value in reversed(values):
            tail.next = ListNode(value)
            tail = tail.next
        return dummy.next
