import java.util.ArrayList;
import java.util.List;

class Solution {
    public TreeNode inorderSuccessor(TreeNode root, TreeNode p) {
        List<TreeNode> nodes = new ArrayList<>();
        inorder(root, nodes);
        for (int i = 0; i + 1 < nodes.size(); i++) {
            if (nodes.get(i) == p) {
                return nodes.get(i + 1);
            }
        }
        return null;
    }

    private void inorder(TreeNode node, List<TreeNode> nodes) {
        if (node == null) {
            return;
        }
        inorder(node.left, nodes);
        nodes.add(node);
        inorder(node.right, nodes);
    }
}
