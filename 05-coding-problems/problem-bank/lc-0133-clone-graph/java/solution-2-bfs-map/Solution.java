import java.util.ArrayDeque;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Queue;

class Solution {
    public Node cloneGraph(Node node) {
        if (node == null) {
            return null;
        }
        Map<Node, Node> clones = new IdentityHashMap<>();
        Queue<Node> queue = new ArrayDeque<>();
        clones.put(node, new Node(node.val));
        queue.add(node);

        while (!queue.isEmpty()) {
            Node current = queue.remove();
            Node copied = clones.get(current);
            for (Node neighbor : current.neighbors) {
                if (!clones.containsKey(neighbor)) {
                    clones.put(neighbor, new Node(neighbor.val));
                    queue.add(neighbor);
                }
                copied.neighbors.add(clones.get(neighbor));
            }
        }
        return clones.get(node);
    }
}
