class Solution {
    public int calculate(String s) {
        Parser parser = new Parser(s);
        return parser.parseExpression();
    }

    private static class Parser {
        private final String text;
        private int index;

        Parser(String text) {
            this.text = text;
            this.index = 0;
        }

        int parseExpression() {
            int result = 0;
            int sign = 1;
            while (index < text.length()) {
                char ch = text.charAt(index);
                if (ch == ' ') {
                    index++;
                } else if (ch == '+') {
                    sign = 1;
                    index++;
                } else if (ch == '-') {
                    sign = -1;
                    index++;
                } else if (ch == '(') {
                    index++;
                    result += sign * parseExpression();
                } else if (ch == ')') {
                    index++;
                    break;
                } else {
                    int number = 0;
                    while (index < text.length() && Character.isDigit(text.charAt(index))) {
                        number = number * 10 + (text.charAt(index) - '0');
                        index++;
                    }
                    result += sign * number;
                }
            }
            return result;
        }
    }
}
