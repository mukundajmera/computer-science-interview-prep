from typing import List, Optional


class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        left = self._digits(l1)
        right = self._digits(l2)
        carry = 0
        index = 0
        dummy = ListNode(0)
        tail = dummy

        while index < len(left) or index < len(right) or carry:
            total = carry
            if index < len(left):
                total += left[index]
            if index < len(right):
                total += right[index]
            tail.next = ListNode(total % 10)
            tail = tail.next
            carry = total // 10
            index += 1
        return dummy.next

    def _digits(self, node: Optional[ListNode]) -> List[int]:
        values: List[int] = []
        while node is not None:
            values.append(node.val)
            node = node.next
        return values
