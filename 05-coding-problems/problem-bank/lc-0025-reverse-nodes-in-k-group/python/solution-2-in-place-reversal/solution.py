from typing import Optional


class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        group_prev = dummy

        def kth_node(node: ListNode, steps: int) -> Optional[ListNode]:
            while node is not None and steps > 0:
                node = node.next
                steps -= 1
            return node

        while True:
            kth = kth_node(group_prev, k)
            if kth is None:
                break
            group_next = kth.next
            prev = group_next
            current = group_prev.next
            while current is not group_next:
                following = current.next
                current.next = prev
                prev = current
                current = following
            old_start = group_prev.next
            group_prev.next = kth
            group_prev = old_start
        return dummy.next
