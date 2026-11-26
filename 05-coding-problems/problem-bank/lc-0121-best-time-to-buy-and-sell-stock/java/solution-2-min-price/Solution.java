class Solution {
    public int maxProfit(int[] prices) {
        int best = 0;
        int minPrice = prices.length == 0 ? 0 : prices[0];
        for (int price : prices) {
            best = Math.max(best, price - minPrice);
            minPrice = Math.min(minPrice, price);
        }
        return best;
    }
}
