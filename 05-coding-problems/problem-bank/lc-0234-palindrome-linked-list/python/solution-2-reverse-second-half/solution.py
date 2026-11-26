from typing import Optional


class Solution:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        slow = head
        fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
        if fast is not None:
            slow = slow.next

        second_head = self._reverse(slow)
        second = second_head
        first = head
        palindrome = True
        while second is not None:
            if first.val != second.val:
                palindrome = False
                break
            first = first.next
            second = second.next
        self._reverse(second_head)
        return palindrome

    def _reverse(self, node: Optional[ListNode]) -> Optional[ListNode]:
        previous = None
        while node is not None:
            following = node.next
            node.next = previous
            previous = node
            node = following
        return previous
