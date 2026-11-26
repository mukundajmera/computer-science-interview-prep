class Solution {
    public TreeNode upsideDownBinaryTree(TreeNode root) {
        TreeNode curr = root;
        TreeNode prev = null;
        TreeNode prevRight = null;

        while (curr != null) {
            TreeNode next = curr.left;
            curr.left = prevRight;
            prevRight = curr.right;
            curr.right = prev;

            prev = curr;
            curr = next;
        }

        return prev;
    }
}
