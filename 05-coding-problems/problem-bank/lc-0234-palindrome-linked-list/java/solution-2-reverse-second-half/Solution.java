class Solution {
    public boolean isPalindrome(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        if (fast != null) {
            slow = slow.next;
        }

        ListNode secondHead = reverse(slow);
        ListNode second = secondHead;
        ListNode first = head;
        boolean palindrome = true;
        while (second != null) {
            if (first.val != second.val) {
                palindrome = false;
                break;
            }
            first = first.next;
            second = second.next;
        }
        reverse(secondHead);
        return palindrome;
    }

    private ListNode reverse(ListNode node) {
        ListNode previous = null;
        while (node != null) {
            ListNode next = node.next;
            node.next = previous;
            previous = node;
            node = next;
        }
        return previous;
    }
}
