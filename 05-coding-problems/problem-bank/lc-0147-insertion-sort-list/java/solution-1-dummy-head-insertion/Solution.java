import java.util.*;

class Solution {
    public ListNode insertionSortList(ListNode head) {
        if (head == null || head.next == null) {
            return head;
        }

        ListNode dummy = new ListNode(0);
        dummy.next = head;
        ListNode curr = head;

        while (curr != null && curr.next != null) {
            if (curr.val <= curr.next.val) {
                curr = curr.next;
            } else {
                ListNode toInsert = curr.next;
                curr.next = toInsert.next;

                ListNode prev = dummy;
                while (prev.next.val < toInsert.val) {
                    prev = prev.next;
                }
                toInsert.next = prev.next;
                prev.next = toInsert;
            }
        }

        return dummy.next;
    }
}
