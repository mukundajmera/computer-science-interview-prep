import java.util.ArrayList;
import java.util.List;

class Solution {
    public ListNode partition(ListNode head, int x) {
        List<ListNode> less = new ArrayList<>();
        List<ListNode> greaterOrEqual = new ArrayList<>();

        while (head != null) {
            ListNode next = head.next;
            head.next = null;
            if (head.val < x) {
                less.add(head);
            } else {
                greaterOrEqual.add(head);
            }
            head = next;
        }

        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        for (ListNode node : less) {
            tail.next = node;
            tail = tail.next;
        }
        for (ListNode node : greaterOrEqual) {
            tail.next = node;
            tail = tail.next;
        }
        return dummy.next;
    }
}
