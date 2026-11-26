import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    public boolean isSymmetric(TreeNode root) {
        if (root == null) {
            return true;
        }
        Queue<TreeNode[]> queue = new ArrayDeque<>();
        queue.add(new TreeNode[] {root.left, root.right});
        while (!queue.isEmpty()) {
            TreeNode[] pair = queue.remove();
            TreeNode left = pair[0];
            TreeNode right = pair[1];
            if (left == null || right == null) {
                if (left != right) {
                    return false;
                }
                continue;
            }
            if (left.val != right.val) {
                return false;
            }
            queue.add(new TreeNode[] {left.left, right.right});
            queue.add(new TreeNode[] {left.right, right.left});
        }
        return true;
    }
}
