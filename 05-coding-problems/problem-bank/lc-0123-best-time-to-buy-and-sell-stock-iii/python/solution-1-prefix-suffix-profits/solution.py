from __future__ import annotations


class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        if len(prices) < 2:
            return 0

        left = [0] * len(prices)
        min_price = prices[0]
        for i in range(1, len(prices)):
            min_price = min(min_price, prices[i])
            left[i] = max(left[i - 1], prices[i] - min_price)

        right = [0] * len(prices)
        max_price = prices[-1]
        for i in range(len(prices) - 2, -1, -1):
            max_price = max(max_price, prices[i])
            right[i] = max(right[i + 1], max_price - prices[i])

        return max(left[i] + right[i] for i in range(len(prices)))
