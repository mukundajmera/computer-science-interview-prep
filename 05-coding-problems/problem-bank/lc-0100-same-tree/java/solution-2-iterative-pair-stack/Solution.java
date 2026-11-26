import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public boolean isSameTree(TreeNode p, TreeNode q) {
        Deque<TreeNode[]> stack = new ArrayDeque<>();
        stack.push(new TreeNode[] {p, q});
        while (!stack.isEmpty()) {
            TreeNode[] pair = stack.pop();
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
            stack.push(new TreeNode[] {left.left, right.left});
            stack.push(new TreeNode[] {left.right, right.right});
        }
        return true;
    }
}
