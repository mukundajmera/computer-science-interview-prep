import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int kthSmallest(TreeNode root, int k) {
        Deque<TreeNode> stack = new ArrayDeque<>();
        TreeNode current = root;
        int remaining = k;
        while (current != null || !stack.isEmpty()) {
            while (current != null) {
                stack.addLast(current);
                current = current.left;
            }
            current = stack.removeLast();
            remaining--;
            if (remaining == 0) {
                return current.val;
            }
            current = current.right;
        }
        throw new IllegalArgumentException("k is larger than the tree size");
    }
}
