class Solution {
    public ListNode rotateRight(ListNode head, int k) {
        if (head == null || head.next == null || k == 0) {
            return head;
        }

        int length = 1;
        ListNode tail = head;
        while (tail.next != null) {
            tail = tail.next;
            length++;
        }

        int shift = k % length;
        if (shift == 0) {
            return head;
        }

        tail.next = head;
        int stepsToNewTail = length - shift;
        ListNode newTail = tail;
        while (stepsToNewTail > 0) {
            newTail = newTail.next;
            stepsToNewTail--;
        }
        ListNode newHead = newTail.next;
        newTail.next = null;
        return newHead;
    }
}
