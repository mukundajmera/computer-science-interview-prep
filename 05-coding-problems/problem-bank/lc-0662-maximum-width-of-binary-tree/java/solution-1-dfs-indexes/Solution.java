import java.util.HashMap;
import java.util.Map;

class Solution {
    public int widthOfBinaryTree(TreeNode root) {
        Map<Integer, Long> firstAtDepth = new HashMap<>();
        return (int) dfs(root, 0, 0L, firstAtDepth);
    }

    private long dfs(TreeNode node, int depth, long index, Map<Integer, Long> firstAtDepth) {
        if (node == null) {
            return 0L;
        }
        firstAtDepth.putIfAbsent(depth, index);
        long current = index - firstAtDepth.get(depth) + 1;
        long left = dfs(node.left, depth + 1, index * 2, firstAtDepth);
        long right = dfs(node.right, depth + 1, index * 2 + 1, firstAtDepth);
        return Math.max(current, Math.max(left, right));
    }
}
