import java.util.ArrayList;
import java.util.List;

class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        List<Integer> left = digits(l1);
        List<Integer> right = digits(l2);
        int carry = 0;
        int index = 0;
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;

        while (index < left.size() || index < right.size() || carry != 0) {
            int total = carry;
            if (index < left.size()) {
                total += left.get(index);
            }
            if (index < right.size()) {
                total += right.get(index);
            }
            tail.next = new ListNode(total % 10);
            tail = tail.next;
            carry = total / 10;
            index++;
        }
        return dummy.next;
    }

    private List<Integer> digits(ListNode node) {
        List<Integer> values = new ArrayList<>();
        while (node != null) {
            values.add(node.val);
            node = node.next;
        }
        return values;
    }
}
