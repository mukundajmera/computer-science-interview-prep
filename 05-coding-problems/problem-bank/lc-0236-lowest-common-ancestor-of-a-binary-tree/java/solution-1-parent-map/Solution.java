import java.util.ArrayDeque;
import java.util.Collections;
import java.util.HashMap;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        Map<TreeNode, TreeNode> parentByNode = new HashMap<>();
        Queue<TreeNode> queue = new ArrayDeque<>();
        parentByNode.put(root, null);
        queue.add(root);

        while (!parentByNode.containsKey(p) || !parentByNode.containsKey(q)) {
            TreeNode node = queue.remove();
            if (node.left != null) {
                parentByNode.put(node.left, node);
                queue.add(node.left);
            }
            if (node.right != null) {
                parentByNode.put(node.right, node);
                queue.add(node.right);
            }
        }

        Set<TreeNode> pAncestors = Collections.newSetFromMap(new IdentityHashMap<>());
        TreeNode current = p;
        while (current != null) {
            pAncestors.add(current);
            current = parentByNode.get(current);
        }

        current = q;
        while (!pAncestors.contains(current)) {
            current = parentByNode.get(current);
        }
        return current;
    }
}
