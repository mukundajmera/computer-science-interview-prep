import java.util.Arrays;

class Solution {
    public int coinChange(int[] coins, int amount) {
        int sentinel = amount + 1;
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, sentinel);
        dp[0] = 0;
        for (int value = 1; value <= amount; value++) {
            for (int coin : coins) {
                if (coin <= value) {
                    dp[value] = Math.min(dp[value], dp[value - coin] + 1);
                }
            }
        }
        return dp[amount] == sentinel ? -1 : dp[amount];
    }
}
