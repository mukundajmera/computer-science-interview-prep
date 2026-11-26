import java.util.HashMap;
import java.util.Map;

class Solution {
    private int[] postorder;
    private Map<Integer, Integer> inorderIndex;

    public TreeNode buildTree(int[] inorder, int[] postorder) {
        this.postorder = postorder;
        this.inorderIndex = new HashMap<>();
        for (int i = 0; i < inorder.length; i++) {
            inorderIndex.put(inorder[i], i);
        }
        return build(0, inorder.length - 1, 0, postorder.length - 1);
    }

    private TreeNode build(int inLeft, int inRight, int postLeft, int postRight) {
        if (inLeft > inRight) {
            return null;
        }
        int rootValue = postorder[postRight];
        int rootIndex = inorderIndex.get(rootValue);
        int leftSize = rootIndex - inLeft;
        TreeNode root = new TreeNode(rootValue);
        root.left = build(inLeft, rootIndex - 1, postLeft, postLeft + leftSize - 1);
        root.right = build(rootIndex + 1, inRight, postLeft + leftSize, postRight - 1);
        return root;
    }
}
