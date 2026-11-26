from typing import Optional


class Solution:
    def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        length = 0
        cursor = head
        while cursor is not None:
            length += 1
            cursor = cursor.next

        steps = length // 2
        cursor = head
        while steps > 0:
            cursor = cursor.next
            steps -= 1
        return cursor
