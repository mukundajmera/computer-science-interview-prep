from typing import Optional


class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if head is None or head.next is None or k == 0:
            return head

        length = 1
        tail = head
        while tail.next is not None:
            tail = tail.next
            length += 1

        shift = k % length
        if shift == 0:
            return head

        tail.next = head
        steps_to_new_tail = length - shift
        new_tail = tail
        for _ in range(steps_to_new_tail):
            new_tail = new_tail.next
        new_head = new_tail.next
        new_tail.next = None
        return new_head
