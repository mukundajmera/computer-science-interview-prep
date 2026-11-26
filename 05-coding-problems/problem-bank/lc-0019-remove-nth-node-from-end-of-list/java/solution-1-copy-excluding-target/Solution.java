import java.util.ArrayList;
import java.util.List;

class Solution {
    public ListNode removeNthFromEnd(ListNode head, int n) {
        List<Integer> values = new ArrayList<>();
        while (head != null) {
            values.add(head.val);
            head = head.next;
        }

        int removeIndex = values.size() - n;
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        for (int i = 0; i < values.size(); i++) {
            if (i == removeIndex) {
                continue;
            }
            tail.next = new ListNode(values.get(i));
            tail = tail.next;
        }
        return dummy.next;
    }
}
