import java.util.ArrayList;
import java.util.List;

class Solution {
    public void reorderList(ListNode head) {
        List<ListNode> nodes = new ArrayList<>();
        for (ListNode current = head; current != null; current = current.next) {
            nodes.add(current);
        }
        int left = 0;
        int right = nodes.size() - 1;
        List<ListNode> order = new ArrayList<>();
        while (left <= right) {
            order.add(nodes.get(left++));
            if (left <= right) {
                order.add(nodes.get(right--));
            }
        }
        for (int i = 0; i + 1 < order.size(); i++) {
            order.get(i).next = order.get(i + 1);
        }
        if (!order.isEmpty()) {
            order.get(order.size() - 1).next = null;
        }
    }
}
