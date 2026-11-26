import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int sumNumbers(TreeNode root) {
        if (root == null) {
            return 0;
        }
        int total = 0;
        Deque<TreeNode> nodes = new ArrayDeque<>();
        Deque<Integer> values = new ArrayDeque<>();
        nodes.addLast(root);
        values.addLast(root.val);
        while (!nodes.isEmpty()) {
            TreeNode node = nodes.removeLast();
            int value = values.removeLast();
            if (node.left == null && node.right == null) {
                total += value;
            }
            if (node.right != null) {
                nodes.addLast(node.right);
                values.addLast(value * 10 + node.right.val);
            }
            if (node.left != null) {
                nodes.addLast(node.left);
                values.addLast(value * 10 + node.left.val);
            }
        }
        return total;
    }
}
