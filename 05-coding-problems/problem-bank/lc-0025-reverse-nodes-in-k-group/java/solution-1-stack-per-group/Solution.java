import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public ListNode reverseKGroup(ListNode head, int k) {
        if (k <= 1 || head == null) {
            return head;
        }
        ListNode dummy = new ListNode(0, head);
        ListNode groupPrev = dummy;
        ListNode current = head;
        while (current != null) {
            Deque<ListNode> stack = new ArrayDeque<>();
            ListNode scan = current;
            for (int i = 0; i < k && scan != null; i++) {
                stack.push(scan);
                scan = scan.next;
            }
            if (stack.size() < k) {
                break;
            }
            while (!stack.isEmpty()) {
                groupPrev.next = stack.pop();
                groupPrev = groupPrev.next;
            }
            groupPrev.next = scan;
            current = scan;
        }
        return dummy.next;
    }
}
