import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<Integer> rightSideView(TreeNode root) {
        List<Integer> view = new ArrayList<>();
        dfs(root, 0, view);
        return view;
    }

    private void dfs(TreeNode node, int depth, List<Integer> view) {
        if (node == null) {
            return;
        }
        if (depth == view.size()) {
            view.add(node.val);
        }
        dfs(node.right, depth + 1, view);
        dfs(node.left, depth + 1, view);
    }
}
