class Solution {
    public int calculate(String s) {
        int total = 0;
        int lastTerm = 0;
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
            if (operation == '+') {
                total += lastTerm;
                lastTerm = number;
            } else if (operation == '-') {
                total += lastTerm;
                lastTerm = -number;
            } else if (operation == '*') {
                lastTerm *= number;
            } else {
                lastTerm /= number;
            }
            operation = current;
            number = 0;
        }
        return total + lastTerm;
    }
}
