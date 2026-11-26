class Solution {
    public ListNode middleNode(ListNode head) {
        int length = 0;
        ListNode cursor = head;
        while (cursor != null) {
            length++;
            cursor = cursor.next;
        }

        int steps = length / 2;
        cursor = head;
        while (steps > 0) {
            cursor = cursor.next;
            steps--;
        }
        return cursor;
    }
}
