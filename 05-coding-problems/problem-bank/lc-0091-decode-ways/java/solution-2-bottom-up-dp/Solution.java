class Solution {
    public int numDecodings(String s) {
        int[] dp = new int[s.length() + 1];
        dp[s.length()] = 1;
        for (int index = s.length() - 1; index >= 0; index--) {
            if (s.charAt(index) == '0') {
                dp[index] = 0;
                continue;
            }
            dp[index] = dp[index + 1];
            if (index + 1 < s.length()) {
                int value = (s.charAt(index) - '0') * 10 + (s.charAt(index + 1) - '0');
                if (value <= 26) {
                    dp[index] += dp[index + 2];
                }
            }
        }
        return dp[0];
    }
}
