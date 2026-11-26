import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    public Node connect(Node root) {
        if (root == null) {
            return null;
        }
        Queue<Node> queue = new ArrayDeque<>();
        queue.add(root);
        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            Node previous = null;
            for (int index = 0; index < levelSize; index++) {
                Node node = queue.remove();
                if (previous != null) {
                    previous.next = node;
                }
                previous = node;
                if (node.left != null) {
                    queue.add(node.left);
                }
                if (node.right != null) {
                    queue.add(node.right);
                }
            }
            if (previous != null) {
                previous.next = null;
            }
        }
        return root;
    }
}
