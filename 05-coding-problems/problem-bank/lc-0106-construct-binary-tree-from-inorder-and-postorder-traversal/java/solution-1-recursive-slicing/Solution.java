import java.util.Arrays;

class Solution {
    public TreeNode buildTree(int[] inorder, int[] postorder) {
        if (inorder.length == 0) {
            return null;
        }
        int rootValue = postorder[postorder.length - 1];
        int rootIndex = 0;
        while (inorder[rootIndex] != rootValue) {
            rootIndex++;
        }
        TreeNode root = new TreeNode(rootValue);
        root.left = buildTree(
            Arrays.copyOfRange(inorder, 0, rootIndex),
            Arrays.copyOfRange(postorder, 0, rootIndex)
        );
        root.right = buildTree(
            Arrays.copyOfRange(inorder, rootIndex + 1, inorder.length),
            Arrays.copyOfRange(postorder, rootIndex, postorder.length - 1)
        );
        return root;
    }
}
