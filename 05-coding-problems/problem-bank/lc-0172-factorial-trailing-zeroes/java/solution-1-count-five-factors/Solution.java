class Solution {
    public int trailingZeroes(int n) {
        int zeroes = 0;
        for (long value = 5; value <= n; value += 5) {
            long current = value;
            while (current % 5 == 0) {
                zeroes++;
                current /= 5;
            }
        }
        return zeroes;
    }
}
