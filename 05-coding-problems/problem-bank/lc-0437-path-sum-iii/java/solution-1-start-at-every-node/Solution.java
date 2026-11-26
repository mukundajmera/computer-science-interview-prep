class Solution {
    public int pathSum(TreeNode root, int targetSum) {
        if (root == null) {
            return 0;
        }
        return countFrom(root, targetSum) + pathSum(root.left, targetSum) + pathSum(root.right, targetSum);
    }

    private int countFrom(TreeNode node, long remaining) {
        if (node == null) {
            return 0;
        }
        int count = node.val == remaining ? 1 : 0;
        count += countFrom(node.left, remaining - node.val);
        count += countFrom(node.right, remaining - node.val);
        return count;
    }
}
