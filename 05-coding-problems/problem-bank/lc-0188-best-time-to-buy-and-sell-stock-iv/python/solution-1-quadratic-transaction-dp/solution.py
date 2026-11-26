from __future__ import annotations


class Solution:
    def maxProfit(self, k: int, prices: list[int]) -> int:
        if k == 0 or len(prices) < 2:
            return 0
        if k >= len(prices) // 2:
            return self._unlimited_profit(prices)

        dp = [[0] * len(prices) for _ in range(k + 1)]
        for transaction in range(1, k + 1):
            for sell in range(1, len(prices)):
                dp[transaction][sell] = dp[transaction][sell - 1]
                for buy in range(sell):
                    profit = dp[transaction - 1][buy] + prices[sell] - prices[buy]
                    dp[transaction][sell] = max(dp[transaction][sell], profit)
        return dp[k][-1]

    def _unlimited_profit(self, prices: list[int]) -> int:
        return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices)))
