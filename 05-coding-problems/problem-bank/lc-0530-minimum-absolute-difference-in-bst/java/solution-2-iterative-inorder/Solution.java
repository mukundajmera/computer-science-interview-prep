import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int getMinimumDifference(TreeNode root) {
        Deque<TreeNode> stack = new ArrayDeque<>();
        TreeNode current = root;
        Integer previous = null;
        int best = Integer.MAX_VALUE;
        while (current != null || !stack.isEmpty()) {
            while (current != null) {
                stack.addLast(current);
                current = current.left;
            }
            current = stack.removeLast();
            if (previous != null) {
                best = Math.min(best, current.val - previous);
            }
            previous = current.val;
            current = current.right;
        }
        return best;
    }
}
