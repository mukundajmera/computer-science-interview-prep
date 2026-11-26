class Solution {
    public ListNode deleteDuplicates(ListNode head) {
        ListNode dummy = new ListNode(0, head);
        ListNode prev = dummy;
        ListNode current = head;
        while (current != null) {
            boolean duplicate = false;
            while (current.next != null && current.val == current.next.val) {
                duplicate = true;
                current = current.next;
            }
            if (duplicate) {
                prev.next = current.next;
            } else {
                prev = prev.next;
            }
            current = current.next;
        }
        return dummy.next;
    }
}
