class Solution:
    def numTrees(self, n: int) -> int:
        dp = [0] * (n + 1)
        dp[0] = 1
        if n >= 1:
            dp[1] = 1
        for size in range(2, n + 1):
            for left in range(size):
                dp[size] += dp[left] * dp[size - 1 - left]
        return dp[n]
