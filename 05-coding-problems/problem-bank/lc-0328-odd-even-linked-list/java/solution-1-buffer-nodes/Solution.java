import java.util.ArrayList;
import java.util.List;

class Solution {
    public ListNode oddEvenList(ListNode head) {
        if (head == null) {
            return null;
        }
        List<ListNode> nodes = new ArrayList<>();
        ListNode current = head;
        int index = 1;
        while (current != null) {
            ListNode next = current.next;
            if (index % 2 == 1) {
                nodes.add(current);
            }
            current = next;
            index++;
        }
        current = head.next;
        index = 2;
        while (current != null) {
            ListNode next = current.next;
            if (index % 2 == 0) {
                nodes.add(current);
            }
            current = next;
            index++;
        }
        for (int i = 0; i + 1 < nodes.size(); i++) {
            nodes.get(i).next = nodes.get(i + 1);
        }
        nodes.get(nodes.size() - 1).next = null;
        return nodes.get(0);
    }
}
