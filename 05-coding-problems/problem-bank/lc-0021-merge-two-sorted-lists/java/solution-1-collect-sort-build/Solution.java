import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

class Solution {
    public ListNode mergeTwoLists(ListNode list1, ListNode list2) {
        List<Integer> values = new ArrayList<>();
        collect(list1, values);
        collect(list2, values);
        Collections.sort(values);

        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        for (int value : values) {
            tail.next = new ListNode(value);
            tail = tail.next;
        }
        return dummy.next;
    }

    private void collect(ListNode node, List<Integer> values) {
        while (node != null) {
            values.add(node.val);
            node = node.next;
        }
    }
}
