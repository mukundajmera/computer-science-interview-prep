from typing import Optional


class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        if head is None or left == right:
            return head

        dummy = ListNode(0)
        dummy.next = head
        before = dummy
        for _ in range(1, left):
            before = before.next

        segment_head = before.next
        segment_tail = segment_head
        for _ in range(left, right):
            segment_tail = segment_tail.next

        after = segment_tail.next
        segment_tail.next = None
        before.next = self._reverse(segment_head)
        segment_head.next = after
        return dummy.next

    def _reverse(self, node: Optional[ListNode]) -> Optional[ListNode]:
        previous = None
        while node is not None:
            following = node.next
            node.next = previous
            previous = node
            node = following
        return previous
