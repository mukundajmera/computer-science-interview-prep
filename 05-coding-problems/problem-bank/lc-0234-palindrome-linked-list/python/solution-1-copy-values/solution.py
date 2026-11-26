from typing import List, Optional


class Solution:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        values: List[int] = []
        while head is not None:
            values.append(head.val)
            head = head.next

        left = 0
        right = len(values) - 1
        while left < right:
            if values[left] != values[right]:
                return False
            left += 1
            right -= 1
        return True
