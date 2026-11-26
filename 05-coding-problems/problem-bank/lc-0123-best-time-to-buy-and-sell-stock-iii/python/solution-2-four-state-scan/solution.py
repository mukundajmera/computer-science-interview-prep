from __future__ import annotations


class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        buy_one = -10**18
        sell_one = 0
        buy_two = -10**18
        sell_two = 0

        for price in prices:
            buy_one = max(buy_one, -price)
            sell_one = max(sell_one, buy_one + price)
            buy_two = max(buy_two, sell_one - price)
            sell_two = max(sell_two, buy_two + price)

        return sell_two
