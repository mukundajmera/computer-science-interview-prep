import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public boolean isBalanced(TreeNode root) {
        if (root == null) {
            return true;
        }
        Deque<TreeNode> stack = new ArrayDeque<>();
        stack.push(root);
        while (!stack.isEmpty()) {
            TreeNode node = stack.pop();
            if (Math.abs(height(node.left) - height(node.right)) > 1) {
                return false;
            }
            if (node.left != null) {
                stack.push(node.left);
            }
            if (node.right != null) {
                stack.push(node.right);
            }
        }
        return true;
    }

    private int height(TreeNode node) {
        if (node == null) {
            return 0;
        }
        int best = 0;
        Deque<NodeDepth> stack = new ArrayDeque<>();
        stack.push(new NodeDepth(node, 1));
        while (!stack.isEmpty()) {
            NodeDepth current = stack.pop();
            best = Math.max(best, current.depth);
            if (current.node.left != null) {
                stack.push(new NodeDepth(current.node.left, current.depth + 1));
            }
            if (current.node.right != null) {
                stack.push(new NodeDepth(current.node.right, current.depth + 1));
            }
        }
        return best;
    }

    private static class NodeDepth {
        private final TreeNode node;
        private final int depth;

        private NodeDepth(TreeNode node, int depth) {
            this.node = node;
            this.depth = depth;
        }
    }
}
