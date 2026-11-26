import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

class Solution {
    public List<List<Integer>> zigzagLevelOrder(TreeNode root) {
        List<List<Integer>> levels = new ArrayList<>();
        dfs(root, 0, levels);
        return levels;
    }

    private void dfs(TreeNode node, int depth, List<List<Integer>> levels) {
        if (node == null) {
            return;
        }
        if (depth == levels.size()) {
            levels.add(new LinkedList<>());
        }
        LinkedList<Integer> level = (LinkedList<Integer>) levels.get(depth);
        if (depth % 2 == 0) {
            level.addLast(node.val);
        } else {
            level.addFirst(node.val);
        }
        dfs(node.left, depth + 1, levels);
        dfs(node.right, depth + 1, levels);
    }
}
