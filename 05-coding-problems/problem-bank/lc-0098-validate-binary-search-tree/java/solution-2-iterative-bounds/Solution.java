import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    private static class Frame {
        TreeNode node;
        long low;
        long high;

        Frame(TreeNode node, long low, long high) {
            this.node = node;
            this.low = low;
            this.high = high;
        }
    }

    public boolean isValidBST(TreeNode root) {
        Deque<Frame> stack = new ArrayDeque<>();
        stack.addLast(new Frame(root, Long.MIN_VALUE, Long.MAX_VALUE));
        while (!stack.isEmpty()) {
            Frame frame = stack.removeLast();
            if (frame.node == null) {
                continue;
            }
            if (frame.node.val <= frame.low || frame.node.val >= frame.high) {
                return false;
            }
            stack.addLast(new Frame(frame.node.right, frame.node.val, frame.high));
            stack.addLast(new Frame(frame.node.left, frame.low, frame.node.val));
        }
        return true;
    }
}
