class Solution {
    public int numTrees(int n) {
        int[] dp = new int[n + 1];
        dp[0] = 1;
        if (n >= 1) dp[1] = 1;
        for (int size = 2; size <= n; size++) {
            for (int left = 0; left < size; left++) dp[size] += dp[left] * dp[size - 1 - left];
        }
        return dp[n];
    }
}
