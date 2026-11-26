class Solution {
    public int maxProfit(int[] prices) {
        int cash = 0;
        int hold = -prices[0];
        for (int index = 1; index < prices.length; index++) {
            int previousCash = cash;
            cash = Math.max(cash, hold + prices[index]);
            hold = Math.max(hold, previousCash - prices[index]);
        }
        return cash;
    }
}
