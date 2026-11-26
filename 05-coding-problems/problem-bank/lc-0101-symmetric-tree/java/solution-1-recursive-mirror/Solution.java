class Solution {
    public boolean isSymmetric(TreeNode root) {
        return root == null || mirrors(root.left, root.right);
    }

    private boolean mirrors(TreeNode left, TreeNode right) {
        if (left == null || right == null) {
            return left == right;
        }
        return left.val == right.val
            && mirrors(left.left, right.right)
            && mirrors(left.right, right.left);
    }
}
