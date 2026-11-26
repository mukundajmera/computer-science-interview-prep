from typing import List, Optional


class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        values: List[int] = []
        while head is not None:
            values.append(head.val)
            head = head.next

        remove_index = len(values) - n
        dummy = ListNode(0)
        tail = dummy
        for index, value in enumerate(values):
            if index == remove_index:
                continue
            tail.next = ListNode(value)
            tail = tail.next
        return dummy.next
