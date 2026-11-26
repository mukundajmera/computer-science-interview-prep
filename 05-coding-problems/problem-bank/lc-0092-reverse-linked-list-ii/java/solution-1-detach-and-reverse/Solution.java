class Solution {
    public ListNode reverseBetween(ListNode head, int left, int right) {
        if (head == null || left == right) {
            return head;
        }

        ListNode dummy = new ListNode(0);
        dummy.next = head;
        ListNode before = dummy;
        for (int position = 1; position < left; position++) {
            before = before.next;
        }

        ListNode segmentHead = before.next;
        ListNode segmentTail = segmentHead;
        for (int position = left; position < right; position++) {
            segmentTail = segmentTail.next;
        }

        ListNode after = segmentTail.next;
        segmentTail.next = null;
        before.next = reverse(segmentHead);
        segmentHead.next = after;
        return dummy.next;
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
