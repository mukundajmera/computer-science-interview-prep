class Solution {
    public Node copyRandomList(Node head) {
        if (head == null) {
            return null;
        }

        Node current = head;
        while (current != null) {
            Node clone = new Node(current.val);
            clone.next = current.next;
            current.next = clone;
            current = clone.next;
        }

        current = head;
        while (current != null) {
            Node clone = current.next;
            clone.random = current.random == null ? null : current.random.next;
            current = clone.next;
        }

        Node copiedHead = head.next;
        current = head;
        while (current != null) {
            Node clone = current.next;
            current.next = clone.next;
            clone.next = clone.next == null ? null : clone.next.next;
            current = current.next;
        }
        return copiedHead;
    }
}
