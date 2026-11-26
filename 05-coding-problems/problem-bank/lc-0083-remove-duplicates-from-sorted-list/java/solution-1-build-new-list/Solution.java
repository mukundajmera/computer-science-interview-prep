import java.util.ArrayList;
import java.util.List;

class Solution {
    public ListNode deleteDuplicates(ListNode head) {
        List<Integer> values = new ArrayList<>();
        for (ListNode current = head; current != null; current = current.next) {
            if (values.isEmpty() || values.get(values.size() - 1) != current.val) {
                values.add(current.val);
            }
        }
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        for (int value : values) {
            tail.next = new ListNode(value);
            tail = tail.next;
        }
        return dummy.next;
    }
}
