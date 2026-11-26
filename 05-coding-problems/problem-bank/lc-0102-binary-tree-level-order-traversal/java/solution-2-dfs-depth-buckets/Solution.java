import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> levels = new ArrayList<>();
        dfs(root, 0, levels);
        return levels;
    }

    private void dfs(TreeNode node, int depth, List<List<Integer>> levels) {
        if (node == null) {
            return;
        }
        if (depth == levels.size()) {
            levels.add(new ArrayList<>());
        }
        levels.get(depth).add(node.val);
        dfs(node.left, depth + 1, levels);
        dfs(node.right, depth + 1, levels);
    }
}
