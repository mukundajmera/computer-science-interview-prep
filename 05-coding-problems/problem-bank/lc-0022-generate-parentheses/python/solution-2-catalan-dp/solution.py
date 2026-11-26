from typing import List


class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        dp: List[List[str]] = [[""]]
        for pairs in range(1, n + 1):
            current = []
            seen = set()
            for left in range(pairs):
                right = pairs - 1 - left
                for left_text in dp[left]:
                    for right_text in dp[right]:
                        candidate = "(" + left_text + ")" + right_text
                        if candidate not in seen:
                            seen.add(candidate)
                            current.append(candidate)
            dp.append(current)
        return dp[n]
