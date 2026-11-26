import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int evalRPN(String[] tokens) {
        Deque<Integer> stack = new ArrayDeque<>();
        for (String token : tokens) {
            if (isOperator(token)) {
                int right = stack.removeLast();
                int left = stack.removeLast();
                stack.addLast(apply(left, right, token));
            } else {
                stack.addLast(Integer.parseInt(token));
            }
        }
        return stack.removeLast();
    }

    private boolean isOperator(String token) {
        return token.equals("+") || token.equals("-") || token.equals("*") || token.equals("/");
    }

    private int apply(int left, int right, String operator) {
        if (operator.equals("+")) {
            return left + right;
        }
        if (operator.equals("-")) {
            return left - right;
        }
        if (operator.equals("*")) {
            return left * right;
        }
        return left / right;
    }
}
