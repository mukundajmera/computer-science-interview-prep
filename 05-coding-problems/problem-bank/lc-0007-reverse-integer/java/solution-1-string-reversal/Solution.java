class Solution {
    public int reverse(int x) {
        boolean negative = x < 0;
        String digits = String.valueOf(Math.abs((long) x));
        String reversedText = new StringBuilder(digits).reverse().toString();
        long value = Long.parseLong(reversedText);
        if (negative) {
            value = -value;
        }
        if (value < Integer.MIN_VALUE || value > Integer.MAX_VALUE) {
            return 0;
        }
        return (int) value;
    }
}
