import java.util.ArrayList;
import java.util.List;

class Solution {
    public void flatten(TreeNode root) {
        List<TreeNode> nodes = new ArrayList<>();
        collectPreorder(root, nodes);
        for (int index = 0; index < nodes.size(); index++) {
            TreeNode node = nodes.get(index);
            node.left = null;
            node.right = index + 1 < nodes.size() ? nodes.get(index + 1) : null;
        }
    }

    private void collectPreorder(TreeNode node, List<TreeNode> nodes) {
        if (node == null) {
            return;
        }
        nodes.add(node);
        collectPreorder(node.left, nodes);
        collectPreorder(node.right, nodes);
    }
}
