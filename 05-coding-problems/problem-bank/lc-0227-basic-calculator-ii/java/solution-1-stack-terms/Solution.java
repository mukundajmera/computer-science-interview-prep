import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int calculate(String s) {
        Deque<Integer> stack = new ArrayDeque<>();
        int number = 0;
        char operation = '+';
        for (int index = 0; index <= s.length(); index++) {
            char current = index < s.length() ? s.charAt(index) : '+';
            if (index < s.length() && current == ' ') {
                continue;
            }
            if (index < s.length() && Character.isDigit(current)) {
                number = number * 10 + (current - '0');
                continue;
            }
            apply(stack, operation, number);
            operation = current;
            number = 0;
        }
        int total = 0;
        for (int value : stack) {
            total += value;
        }
        return total;
    }

    private void apply(Deque<Integer> stack, char operation, int number) {
        if (operation == '+') {
            stack.push(number);
        } else if (operation == '-') {
            stack.push(-number);
        } else if (operation == '*') {
            stack.push(stack.pop() * number);
        } else {
            stack.push(stack.pop() / number);
        }
    }
}
