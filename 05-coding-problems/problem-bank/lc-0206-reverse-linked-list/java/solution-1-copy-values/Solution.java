import java.util.ArrayList;
import java.util.List;

class Solution {
    public ListNode reverseList(ListNode head) {
        List<Integer> values = new ArrayList<>();
        while (head != null) {
            values.add(head.val);
            head = head.next;
        }

        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        for (int i = values.size() - 1; i >= 0; i--) {
            tail.next = new ListNode(values.get(i));
            tail = tail.next;
        }
        return dummy.next;
    }
}
