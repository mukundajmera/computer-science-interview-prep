import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    private static class Task {
        TreeNode parent;
        int left;
        int right;
        boolean attachLeft;

        Task(TreeNode parent, int left, int right, boolean attachLeft) {
            this.parent = parent;
            this.left = left;
            this.right = right;
            this.attachLeft = attachLeft;
        }
    }

    public TreeNode sortedArrayToBST(int[] nums) {
        if (nums.length == 0) {
            return null;
        }
        int mid = (nums.length - 1) / 2;
        TreeNode root = new TreeNode(nums[mid]);
        Queue<Task> queue = new ArrayDeque<>();
        queue.add(new Task(root, 0, mid - 1, true));
        queue.add(new Task(root, mid + 1, nums.length - 1, false));
        while (!queue.isEmpty()) {
            Task task = queue.remove();
            if (task.left > task.right) {
                continue;
            }
            int childMid = (task.left + task.right) / 2;
            TreeNode child = new TreeNode(nums[childMid]);
            if (task.attachLeft) {
                task.parent.left = child;
            } else {
                task.parent.right = child;
            }
            queue.add(new Task(child, task.left, childMid - 1, true));
            queue.add(new Task(child, childMid + 1, task.right, false));
        }
        return root;
    }
}
