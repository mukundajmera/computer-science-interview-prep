class Solution {
    private int remaining;
    private int answer;
    private boolean found;

    public int kthSmallest(TreeNode root, int k) {
        remaining = k;
        answer = 0;
        found = false;
        inorder(root);
        return answer;
    }

    private void inorder(TreeNode node) {
        if (node == null || found) {
            return;
        }
        inorder(node.left);
        if (found) {
            return;
        }
        remaining--;
        if (remaining == 0) {
            answer = node.val;
            found = true;
            return;
        }
        inorder(node.right);
    }
}
