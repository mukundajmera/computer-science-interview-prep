class Solution {
    private TreeNode first;
    private TreeNode second;
    private TreeNode previous;
    public void recoverTree(TreeNode root) {
        first = null;
        second = null;
        previous = null;
        inorder(root);
        if (first != null && second != null) {
            int temp = first.val;
            first.val = second.val;
            second.val = temp;
        }
    }
    private void inorder(TreeNode node) {
        if (node == null) return;
        inorder(node.left);
        if (previous != null && previous.val > node.val) {
            if (first == null) first = previous;
            second = node;
        }
        previous = node;
        inorder(node.right);
    }
}
