class Solution {
    public ListNode swapPairs(ListNode head) {
        ListNode dummy = new ListNode(0, head);
        ListNode previous = dummy;

        while (previous.next != null && previous.next.next != null) {
            ListNode first = previous.next;
            ListNode second = first.next;
            ListNode after = second.next;

            previous.next = second;
            second.next = first;
            first.next = after;
            previous = first;
        }
        return dummy.next;
    }
}
