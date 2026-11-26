import java.util.HashMap;
import java.util.Map;

class Solution {
    public int pathSum(TreeNode root, int targetSum) {
        Map<Long, Integer> prefixes = new HashMap<>();
        prefixes.put(0L, 1);
        return dfs(root, 0L, targetSum, prefixes);
    }

    private int dfs(TreeNode node, long prefix, int target, Map<Long, Integer> prefixes) {
        if (node == null) {
            return 0;
        }
        long current = prefix + node.val;
        int count = prefixes.getOrDefault(current - target, 0);
        prefixes.put(current, prefixes.getOrDefault(current, 0) + 1);
        count += dfs(node.left, current, target, prefixes);
        count += dfs(node.right, current, target, prefixes);
        int remaining = prefixes.get(current) - 1;
        if (remaining == 0) {
            prefixes.remove(current);
        } else {
            prefixes.put(current, remaining);
        }
        return count;
    }
}
