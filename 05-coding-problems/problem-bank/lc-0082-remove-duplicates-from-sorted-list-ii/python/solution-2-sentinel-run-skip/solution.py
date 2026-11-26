from typing import Optional


class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        prev = dummy
        current = head
        while current is not None:
            duplicate = False
            while current.next is not None and current.val == current.next.val:
                duplicate = True
                current = current.next
            if duplicate:
                prev.next = current.next
            else:
                prev = prev.next
            current = current.next
        return dummy.next
