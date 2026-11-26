import java.util.PriorityQueue;

class Solution {
    public ListNode mergeKLists(ListNode[] lists) {
        PriorityQueue<ListNode> heap = new PriorityQueue<>((left, right) -> Integer.compare(left.val, right.val));
        for (ListNode head : lists) {
            if (head != null) {
                heap.add(head);
            }
        }

        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        while (!heap.isEmpty()) {
            ListNode node = heap.remove();
            if (node.next != null) {
                heap.add(node.next);
            }
            node.next = null;
            tail.next = node;
            tail = tail.next;
        }
        return dummy.next;
    }
}
