import java.util.*;
class Solution {
    public void recoverTree(TreeNode root) {
        List<TreeNode> nodes = new ArrayList<>();
        inorder(root, nodes);
        List<Integer> values = new ArrayList<>();
        for (TreeNode node : nodes) values.add(node.val);
        Collections.sort(values);
        for (int i = 0; i < nodes.size(); i++) nodes.get(i).val = values.get(i);
    }
    private void inorder(TreeNode node, List<TreeNode> nodes) {
        if (node == null) return;
        inorder(node.left, nodes);
        nodes.add(node);
        inorder(node.right, nodes);
    }
}
