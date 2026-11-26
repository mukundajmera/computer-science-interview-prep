import java.util.IdentityHashMap;
import java.util.Map;

class Solution {
    public Node cloneGraph(Node node) {
        return clone(node, new IdentityHashMap<>());
    }

    private Node clone(Node node, Map<Node, Node> clones) {
        if (node == null) {
            return null;
        }
        if (clones.containsKey(node)) {
            return clones.get(node);
        }
        Node copied = new Node(node.val);
        clones.put(node, copied);
        for (Node neighbor : node.neighbors) {
            copied.neighbors.add(clone(neighbor, clones));
        }
        return copied;
    }
}
