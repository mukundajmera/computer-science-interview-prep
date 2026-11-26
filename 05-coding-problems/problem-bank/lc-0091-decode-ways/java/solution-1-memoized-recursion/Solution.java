import java.util.Arrays;

class Solution {
    public int numDecodings(String s) {
        int[] memo = new int[s.length()];
        Arrays.fill(memo, -1);
        return countFrom(0, s, memo);
    }

    private int countFrom(int index, String s, int[] memo) {
        if (index == s.length()) {
            return 1;
        }
        if (s.charAt(index) == '0') {
            return 0;
        }
        if (memo[index] != -1) {
            return memo[index];
        }
        int total = countFrom(index + 1, s, memo);
        if (index + 1 < s.length()) {
            int value = (s.charAt(index) - '0') * 10 + (s.charAt(index + 1) - '0');
            if (value <= 26) {
                total += countFrom(index + 2, s, memo);
            }
        }
        memo[index] = total;
        return total;
    }
}
