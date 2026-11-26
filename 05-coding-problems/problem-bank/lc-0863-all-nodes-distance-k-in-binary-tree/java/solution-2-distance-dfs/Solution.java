import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<Integer> distanceK(TreeNode root, TreeNode target, int k) {
        List<Integer> result = new ArrayList<>();
        distance(root, target, k, result);
        return result;
    }

    private int distance(TreeNode node, TreeNode target, int k, List<Integer> result) {
        if (node == null) {
            return -1;
        }
        if (node == target) {
            collect(node, k, result);
            return 0;
        }
        int left = distance(node.left, target, k, result);
        if (left >= 0) {
            if (left + 1 == k) {
                result.add(node.val);
            } else {
                collect(node.right, k - left - 2, result);
            }
            return left + 1;
        }
        int right = distance(node.right, target, k, result);
        if (right >= 0) {
            if (right + 1 == k) {
                result.add(node.val);
            } else {
                collect(node.left, k - right - 2, result);
            }
            return right + 1;
        }
        return -1;
    }

    private void collect(TreeNode node, int distance, List<Integer> result) {
        if (node == null || distance < 0) {
            return;
        }
        if (distance == 0) {
            result.add(node.val);
            return;
        }
        collect(node.left, distance - 1, result);
        collect(node.right, distance - 1, result);
    }
}
