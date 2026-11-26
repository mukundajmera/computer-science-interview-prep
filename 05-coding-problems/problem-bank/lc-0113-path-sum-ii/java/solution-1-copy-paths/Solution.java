import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<List<Integer>> pathSum(TreeNode root, int targetSum) {
        List<List<Integer>> result = new ArrayList<>();
        dfs(root, targetSum, new ArrayList<>(), result);
        return result;
    }

    private void dfs(TreeNode node, int remaining, List<Integer> path, List<List<Integer>> result) {
        if (node == null) {
            return;
        }
        List<Integer> next = new ArrayList<>(path);
        next.add(node.val);
        if (node.left == null && node.right == null && remaining == node.val) {
            result.add(next);
            return;
        }
        dfs(node.left, remaining - node.val, next, result);
        dfs(node.right, remaining - node.val, next, result);
    }
}
