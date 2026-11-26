class Solution {
    public boolean isSubtree(TreeNode root, TreeNode subRoot) {
        return serialize(root).contains(serialize(subRoot));
    }

    private String serialize(TreeNode node) {
        if (node == null) {
            return "#,";
        }
        return "^" + node.val + "," + serialize(node.left) + serialize(node.right);
    }
}
