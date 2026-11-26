from typing import List, Optional


class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        values: List[int] = []
        for node in (list1, list2):
            while node is not None:
                values.append(node.val)
                node = node.next
        values.sort()

        dummy = ListNode(0)
        tail = dummy
        for value in values:
            tail.next = ListNode(value)
            tail = tail.next
        return dummy.next
