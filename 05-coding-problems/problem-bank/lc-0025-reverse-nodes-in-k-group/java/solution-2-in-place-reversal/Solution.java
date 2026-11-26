class Solution {
    public ListNode reverseKGroup(ListNode head, int k) {
        ListNode dummy = new ListNode(0, head);
        ListNode groupPrev = dummy;
        while (true) {
            ListNode kth = kthNode(groupPrev, k);
            if (kth == null) {
                break;
            }
            ListNode groupNext = kth.next;
            ListNode prev = groupNext;
            ListNode current = groupPrev.next;
            while (current != groupNext) {
                ListNode next = current.next;
                current.next = prev;
                prev = current;
                current = next;
            }
            ListNode oldStart = groupPrev.next;
            groupPrev.next = kth;
            groupPrev = oldStart;
        }
        return dummy.next;
    }

    private ListNode kthNode(ListNode node, int k) {
        while (node != null && k > 0) {
            node = node.next;
            k--;
        }
        return node;
    }
}
