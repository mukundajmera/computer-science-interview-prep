from typing import Optional


class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        nodes = []
        current = head
        while current:
            nodes.append(current)
            current = current.next
        order = []
        left, right = 0, len(nodes) - 1
        while left <= right:
            order.append(nodes[left])
            left += 1
            if left <= right:
                order.append(nodes[right])
                right -= 1
        for index in range(len(order) - 1):
            order[index].next = order[index + 1]
        if order:
            order[-1].next = None
