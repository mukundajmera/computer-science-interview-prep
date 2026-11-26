class Solution {
    public int maxProfit(int[] prices) {
        int buyOne = Integer.MIN_VALUE / 4;
        int sellOne = 0;
        int buyTwo = Integer.MIN_VALUE / 4;
        int sellTwo = 0;

        for (int price : prices) {
            buyOne = Math.max(buyOne, -price);
            sellOne = Math.max(sellOne, buyOne + price);
            buyTwo = Math.max(buyTwo, sellOne - price);
            sellTwo = Math.max(sellTwo, buyTwo + price);
        }

        return sellTwo;
    }
}
