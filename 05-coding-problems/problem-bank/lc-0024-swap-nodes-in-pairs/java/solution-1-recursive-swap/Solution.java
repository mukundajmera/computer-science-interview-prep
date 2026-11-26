class Solution {
    public ListNode swapPairs(ListNode head) {
        if (head == null || head.next == null) {
            return head;
        }

        ListNode second = head.next;
        ListNode remaining = second.next;
        second.next = head;
        head.next = swapPairs(remaining);
        return second;
    }
}
