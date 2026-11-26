import java.util.ArrayList;
import java.util.List;

class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        List<TreeNode> pPath = pathTo(root, p.val);
        List<TreeNode> qPath = pathTo(root, q.val);
        TreeNode answer = root;
        int limit = Math.min(pPath.size(), qPath.size());
        for (int i = 0; i < limit; i++) {
            if (pPath.get(i) != qPath.get(i)) {
                break;
            }
            answer = pPath.get(i);
        }
        return answer;
    }

    private List<TreeNode> pathTo(TreeNode root, int target) {
        List<TreeNode> path = new ArrayList<>();
        TreeNode current = root;
        while (current != null) {
            path.add(current);
            if (target < current.val) {
                current = current.left;
            } else if (target > current.val) {
                current = current.right;
            } else {
                break;
            }
        }
        return path;
    }
}
