import java.util.HashMap;
import java.util.Map;

class Solution {
    private int[] preorder;
    private Map<Integer, Integer> inorderIndex;

    public TreeNode buildTree(int[] preorder, int[] inorder) {
        this.preorder = preorder;
        this.inorderIndex = new HashMap<>();
        for (int i = 0; i < inorder.length; i++) {
            inorderIndex.put(inorder[i], i);
        }
        return build(0, preorder.length - 1, 0, inorder.length - 1);
    }

    private TreeNode build(int preLeft, int preRight, int inLeft, int inRight) {
        if (preLeft > preRight) {
            return null;
        }
        int rootValue = preorder[preLeft];
        int rootIndex = inorderIndex.get(rootValue);
        int leftSize = rootIndex - inLeft;
        TreeNode root = new TreeNode(rootValue);
        root.left = build(preLeft + 1, preLeft + leftSize, inLeft, rootIndex - 1);
        root.right = build(preLeft + leftSize + 1, preRight, rootIndex + 1, inRight);
        return root;
    }
}
