class Solution {
    public int myAtoi(String s) {
        int index = 0;
        int n = s.length();
        while (index < n && s.charAt(index) == ' ') {
            index++;
        }
        int sign = 1;
        if (index < n && (s.charAt(index) == '+' || s.charAt(index) == '-')) {
            sign = s.charAt(index) == '-' ? -1 : 1;
            index++;
        }
        long value = 0;
        long limit = sign == 1 ? Integer.MAX_VALUE : 2147483648L;
        while (index < n && Character.isDigit(s.charAt(index))) {
            value = value * 10 + (s.charAt(index) - '0');
            if (value > limit) {
                return sign == 1 ? Integer.MAX_VALUE : Integer.MIN_VALUE;
            }
            index++;
        }
        return (int) (sign * value);
    }
}
