import java.util.HashMap;
import java.util.Map;

class Solution {
    public ListNode deleteDuplicates(ListNode head) {
        Map<Integer, Integer> counts = new HashMap<>();
        for (ListNode node = head; node != null; node = node.next) {
            counts.put(node.val, counts.getOrDefault(node.val, 0) + 1);
        }
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        for (ListNode node = head; node != null; node = node.next) {
            if (counts.get(node.val) == 1) {
                tail.next = node;
                tail = node;
            }
        }
        tail.next = null;
        return dummy.next;
    }
}
