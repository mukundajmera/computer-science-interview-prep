class Solution {
    public int myAtoi(String s) {
        int state = 0;
        int sign = 1;
        long value = 0;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (state == 0) {
                if (ch == ' ') {
                    continue;
                }
                if (ch == '+' || ch == '-') {
                    sign = ch == '-' ? -1 : 1;
                    state = 1;
                    continue;
                }
                if (!Character.isDigit(ch)) {
                    return 0;
                }
                state = 1;
            }
            if (!Character.isDigit(ch)) {
                break;
            }
            value = value * 10 + (ch - '0');
            long limit = sign == 1 ? Integer.MAX_VALUE : 2147483648L;
            if (value > limit) {
                return sign == 1 ? Integer.MAX_VALUE : Integer.MIN_VALUE;
            }
        }
        return (int) (sign * value);
    }
}
