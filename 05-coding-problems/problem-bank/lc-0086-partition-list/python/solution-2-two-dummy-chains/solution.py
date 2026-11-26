from typing import Optional


class Solution:
    def partition(self, head: Optional[ListNode], x: int) -> Optional[ListNode]:
        before_dummy = ListNode(0)
        after_dummy = ListNode(0)
        before_tail = before_dummy
        after_tail = after_dummy

        while head is not None:
            following = head.next
            head.next = None
            if head.val < x:
                before_tail.next = head
                before_tail = before_tail.next
            else:
                after_tail.next = head
                after_tail = after_tail.next
            head = following
        before_tail.next = after_dummy.next
        return before_dummy.next
