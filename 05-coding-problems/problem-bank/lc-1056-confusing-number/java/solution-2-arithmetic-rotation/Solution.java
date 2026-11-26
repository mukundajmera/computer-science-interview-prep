class Solution {
    public boolean confusingNumber(int n) {
        int original = n;
        int rotated = 0;
        while (n > 0) {
            int digit = n % 10;
            int mapped;
            if (digit == 0 || digit == 1 || digit == 8) {
                mapped = digit;
            } else if (digit == 6) {
                mapped = 9;
            } else if (digit == 9) {
                mapped = 6;
            } else {
                return false;
            }
            rotated = rotated * 10 + mapped;
            n /= 10;
        }
        return rotated != original;
    }
}
