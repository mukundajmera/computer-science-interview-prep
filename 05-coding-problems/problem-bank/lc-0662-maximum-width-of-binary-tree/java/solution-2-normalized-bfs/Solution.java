import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int widthOfBinaryTree(TreeNode root) {
        if (root == null) {
            return 0;
        }
        Deque<NodeIndex> queue = new ArrayDeque<>();
        queue.addLast(new NodeIndex(root, 0L));
        int best = 0;
        while (!queue.isEmpty()) {
            int size = queue.size();
            long offset = queue.peekFirst().index;
            long first = 0L;
            long last = 0L;
            for (int i = 0; i < size; i++) {
                NodeIndex item = queue.removeFirst();
                long normalized = item.index - offset;
                if (i == 0) {
                    first = normalized;
                }
                if (i == size - 1) {
                    last = normalized;
                }
                if (item.node.left != null) {
                    queue.addLast(new NodeIndex(item.node.left, normalized * 2));
                }
                if (item.node.right != null) {
                    queue.addLast(new NodeIndex(item.node.right, normalized * 2 + 1));
                }
            }
            best = Math.max(best, (int) (last - first + 1));
        }
        return best;
    }

    private static class NodeIndex {
        private final TreeNode node;
        private final long index;

        private NodeIndex(TreeNode node, long index) {
            this.node = node;
            this.index = index;
        }
    }
}
