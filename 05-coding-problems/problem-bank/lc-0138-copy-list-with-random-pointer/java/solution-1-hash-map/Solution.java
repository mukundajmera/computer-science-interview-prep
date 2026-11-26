import java.util.IdentityHashMap;
import java.util.Map;

class Solution {
    public Node copyRandomList(Node head) {
        if (head == null) {
            return null;
        }
        Map<Node, Node> clones = new IdentityHashMap<>();
        Node current = head;
        while (current != null) {
            clones.put(current, new Node(current.val));
            current = current.next;
        }
        current = head;
        while (current != null) {
            Node clone = clones.get(current);
            clone.next = clones.get(current.next);
            clone.random = clones.get(current.random);
            current = current.next;
        }
        return clones.get(head);
    }
}
