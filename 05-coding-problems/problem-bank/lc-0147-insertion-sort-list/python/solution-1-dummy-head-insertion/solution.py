from typing import Optional


class Solution:
    def insertionSortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head or not head.next:
            return head

        dummy = ListNode(0)
        dummy.next = head
        curr = head

        while curr and curr.next:
            if curr.val <= curr.next.val:
                curr = curr.next
            else:
                to_insert = curr.next
                curr.next = to_insert.next

                prev = dummy
                while prev.next.val < to_insert.val:
                    prev = prev.next

                to_insert.next = prev.next
                prev.next = to_insert

        return dummy.next
