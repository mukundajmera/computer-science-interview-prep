import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int longestValidParentheses(String s) {
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(-1);
        int best = 0;
        for (int index = 0; index < s.length(); index++) {
            if (s.charAt(index) == '(') {
                stack.push(index);
            } else {
                stack.pop();
                if (stack.isEmpty()) {
                    stack.push(index);
                } else {
                    best = Math.max(best, index - stack.peek());
                }
            }
        }
        return best;
    }
}
