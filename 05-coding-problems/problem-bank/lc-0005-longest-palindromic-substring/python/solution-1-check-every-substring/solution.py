from __future__ import annotations


class Solution:
    def longestPalindrome(self, s: str) -> str:
        for length in range(len(s), 0, -1):
            for start in range(0, len(s) - length + 1):
                candidate = s[start : start + length]
                if candidate == candidate[::-1]:
                    return candidate
        return ""
