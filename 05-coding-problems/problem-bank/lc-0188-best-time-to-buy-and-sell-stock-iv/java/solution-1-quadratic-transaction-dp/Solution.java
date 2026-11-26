class Solution {
    public int maxProfit(int k, int[] prices) {
        int n = prices.length;
        if (k == 0 || n < 2) {
            return 0;
        }
        if (k >= n / 2) {
            return unlimitedProfit(prices);
        }

        int[][] dp = new int[k + 1][n];
        for (int transaction = 1; transaction <= k; transaction++) {
            for (int sell = 1; sell < n; sell++) {
                dp[transaction][sell] = dp[transaction][sell - 1];
                for (int buy = 0; buy < sell; buy++) {
                    int profit = dp[transaction - 1][buy] + prices[sell] - prices[buy];
                    dp[transaction][sell] = Math.max(dp[transaction][sell], profit);
                }
            }
        }
        return dp[k][n - 1];
    }

    private int unlimitedProfit(int[] prices) {
        int profit = 0;
        for (int i = 1; i < prices.length; i++) {
            if (prices[i] > prices[i - 1]) {
                profit += prices[i] - prices[i - 1];
            }
        }
        return profit;
    }
}
