from typing import Optional


class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if head is None or head.next is None or k == 0:
            return head

        length = 1
        tail = head
        while tail.next is not None:
            length += 1
            tail = tail.next

        shift = k % length
        if shift == 0:
            return head

        steps_to_new_tail = length - shift - 1
        new_tail = head
        while steps_to_new_tail > 0:
            new_tail = new_tail.next
            steps_to_new_tail -= 1

        new_head = new_tail.next
        new_tail.next = None
        tail.next = head
        return new_head
