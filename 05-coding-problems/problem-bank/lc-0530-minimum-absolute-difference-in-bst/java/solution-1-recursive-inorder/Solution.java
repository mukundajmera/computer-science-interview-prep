class Solution {
    private Integer previous;
    private int best;

    public int getMinimumDifference(TreeNode root) {
        previous = null;
        best = Integer.MAX_VALUE;
        inorder(root);
        return best;
    }

    private void inorder(TreeNode node) {
        if (node == null) {
            return;
        }
        inorder(node.left);
        if (previous != null) {
            best = Math.min(best, node.val - previous);
        }
        previous = node.val;
        inorder(node.right);
    }
}
