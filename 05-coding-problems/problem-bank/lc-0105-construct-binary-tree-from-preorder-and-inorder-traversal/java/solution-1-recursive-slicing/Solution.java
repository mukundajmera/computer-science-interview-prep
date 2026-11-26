import java.util.Arrays;

class Solution {
    public TreeNode buildTree(int[] preorder, int[] inorder) {
        if (preorder.length == 0) {
            return null;
        }
        int rootValue = preorder[0];
        int rootIndex = 0;
        while (inorder[rootIndex] != rootValue) {
            rootIndex++;
        }
        TreeNode root = new TreeNode(rootValue);
        root.left = buildTree(
            Arrays.copyOfRange(preorder, 1, 1 + rootIndex),
            Arrays.copyOfRange(inorder, 0, rootIndex)
        );
        root.right = buildTree(
            Arrays.copyOfRange(preorder, 1 + rootIndex, preorder.length),
            Arrays.copyOfRange(inorder, rootIndex + 1, inorder.length)
        );
        return root;
    }
}
