import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

class Solution {
    public List<Integer> distanceK(TreeNode root, TreeNode target, int k) {
        Map<TreeNode, TreeNode> parent = new HashMap<>();
        buildParents(root, null, parent);
        Queue<TreeNode> queue = new ArrayDeque<>();
        Set<TreeNode> seen = new HashSet<>();
        queue.add(target);
        seen.add(target);
        int distance = 0;
        while (!queue.isEmpty() && distance < k) {
            for (int size = queue.size(); size > 0; size--) {
                TreeNode node = queue.remove();
                for (TreeNode next : new TreeNode[] {node.left, node.right, parent.get(node)}) {
                    if (next != null && seen.add(next)) {
                        queue.add(next);
                    }
                }
            }
            distance++;
        }
        List<Integer> result = new ArrayList<>();
        while (!queue.isEmpty()) {
            result.add(queue.remove().val);
        }
        return result;
    }

    private void buildParents(TreeNode node, TreeNode par, Map<TreeNode, TreeNode> parent) {
        if (node == null) {
            return;
        }
        parent.put(node, par);
        buildParents(node.left, node, parent);
        buildParents(node.right, node, parent);
    }
}
