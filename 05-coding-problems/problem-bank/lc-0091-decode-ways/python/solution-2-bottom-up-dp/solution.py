class Solution:
    def numDecodings(self, s: str) -> int:
        dp = [0] * (len(s) + 1)
        dp[len(s)] = 1
        for index in range(len(s) - 1, -1, -1):
            if s[index] == "0":
                continue
            dp[index] = dp[index + 1]
            if index + 1 < len(s) and int(s[index:index + 2]) <= 26:
                dp[index] += dp[index + 2]
        return dp[0]
