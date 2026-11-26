from typing import Optional


class Solution:
    def oddEvenList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if head is None:
            return None
        nodes = []
        current = head
        index = 1
        while current:
            next_node = current.next
            if index % 2 == 1:
                nodes.append(current)
            current = next_node
            index += 1

        current = head.next
        index = 2
        while current:
            next_node = current.next
            if index % 2 == 0:
                nodes.append(current)
            current = next_node
            index += 1

        for index in range(len(nodes) - 1):
            nodes[index].next = nodes[index + 1]
        nodes[-1].next = None
        return nodes[0]
