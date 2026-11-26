from typing import Optional


class Solution:
    def partition(self, head: Optional[ListNode], x: int) -> Optional[ListNode]:
        less = []
        greater_or_equal = []

        while head is not None:
            following = head.next
            head.next = None
            if head.val < x:
                less.append(head)
            else:
                greater_or_equal.append(head)
            head = following

        dummy = ListNode(0)
        tail = dummy
        for node in less:
            tail.next = node
            tail = tail.next
        for node in greater_or_equal:
            tail.next = node
            tail = tail.next
        return dummy.next
