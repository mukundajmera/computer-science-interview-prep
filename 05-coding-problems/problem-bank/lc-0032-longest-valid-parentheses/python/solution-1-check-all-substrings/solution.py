class Solution:
    def longestValidParentheses(self, s: str) -> int:
        best = 0
        for start in range(len(s)):
            for end in range(start + 2, len(s) + 1, 2):
                if end - start > best and self._is_valid(s, start, end):
                    best = end - start
        return best

    def _is_valid(self, s: str, start: int, end: int) -> bool:
        balance = 0
        for index in range(start, end):
            balance += 1 if s[index] == "(" else -1
            if balance < 0:
                return False
        return balance == 0
