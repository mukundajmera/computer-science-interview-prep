class Solution {
    public ListNode partition(ListNode head, int x) {
        ListNode beforeDummy = new ListNode(0);
        ListNode afterDummy = new ListNode(0);
        ListNode beforeTail = beforeDummy;
        ListNode afterTail = afterDummy;

        while (head != null) {
            ListNode next = head.next;
            head.next = null;
            if (head.val < x) {
                beforeTail.next = head;
                beforeTail = beforeTail.next;
            } else {
                afterTail.next = head;
                afterTail = afterTail.next;
            }
            head = next;
        }
        beforeTail.next = afterDummy.next;
        return beforeDummy.next;
    }
}
