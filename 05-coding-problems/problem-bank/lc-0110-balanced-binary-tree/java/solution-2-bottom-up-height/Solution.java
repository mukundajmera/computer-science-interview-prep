import java.util.ArrayDeque;
import java.util.Deque;
import java.util.IdentityHashMap;
import java.util.Map;

class Solution {
    public boolean isBalanced(TreeNode root) {
        if (root == null) {
            return true;
        }
        Map<TreeNode, Integer> heights = new IdentityHashMap<>();
        Deque<NodeState> stack = new ArrayDeque<>();
        stack.push(new NodeState(root, false));
        while (!stack.isEmpty()) {
            NodeState state = stack.pop();
            TreeNode node = state.node;
            if (state.visited) {
                int left = heights.getOrDefault(node.left, 0);
                int right = heights.getOrDefault(node.right, 0);
                if (Math.abs(left - right) > 1) {
                    return false;
                }
                heights.put(node, 1 + Math.max(left, right));
                continue;
            }
            stack.push(new NodeState(node, true));
            if (node.right != null) {
                stack.push(new NodeState(node.right, false));
            }
            if (node.left != null) {
                stack.push(new NodeState(node.left, false));
            }
        }
        return true;
    }

    private static class NodeState {
        private final TreeNode node;
        private final boolean visited;

        private NodeState(TreeNode node, boolean visited) {
            this.node = node;
            this.visited = visited;
        }
    }
}
