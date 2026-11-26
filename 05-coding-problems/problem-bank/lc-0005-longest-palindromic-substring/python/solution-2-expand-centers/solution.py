from __future__ import annotations


class Solution:
    def longestPalindrome(self, s: str) -> str:
        best_start = 0
        best_length = 0

        def expand(left: int, right: int) -> int:
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            return right - left - 1

        for center in range(len(s)):
            length = max(expand(center, center), expand(center, center + 1))
            if length > best_length:
                best_length = length
                best_start = center - (length - 1) // 2

        return s[best_start : best_start + best_length]
