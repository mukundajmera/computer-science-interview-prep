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
            int bestBalance = -prices[0];
            for (int day = 1; day < n; day++) {
                dp[transaction][day] = Math.max(dp[transaction][day - 1], prices[day] + bestBalance);
                bestBalance = Math.max(bestBalance, dp[transaction - 1][day] - prices[day]);
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
