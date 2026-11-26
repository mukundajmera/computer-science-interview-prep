import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int calculate(String s) {
        int result = 0;
        int number = 0;
        int sign = 1;
        Deque<Integer> stack = new ArrayDeque<>();
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (Character.isDigit(ch)) {
                number = number * 10 + (ch - '0');
            } else if (ch == '+') {
                result += sign * number;
                number = 0;
                sign = 1;
            } else if (ch == '-') {
                result += sign * number;
                number = 0;
                sign = -1;
            } else if (ch == '(') {
                stack.addLast(result);
                stack.addLast(sign);
                result = 0;
                sign = 1;
            } else if (ch == ')') {
                result += sign * number;
                number = 0;
                int outerSign = stack.removeLast();
                int outerResult = stack.removeLast();
                result = outerResult + outerSign * result;
            }
        }
        return result + sign * number;
    }
}
