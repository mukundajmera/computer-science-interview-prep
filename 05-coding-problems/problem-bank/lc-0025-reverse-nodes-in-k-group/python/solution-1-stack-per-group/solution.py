from typing import Optional


class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if k <= 1 or head is None:
            return head
        dummy = ListNode(0, head)
        group_prev = dummy
        current = head
        while current is not None:
            stack = []
            scan = current
            for _ in range(k):
                if scan is None:
                    return dummy.next
                stack.append(scan)
                scan = scan.next
            while stack:
                group_prev.next = stack.pop()
                group_prev = group_prev.next
            group_prev.next = scan
            current = scan
        return dummy.next
