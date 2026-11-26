from __future__ import annotations


class Solution:
    def longestPalindrome(self, s: str) -> str:
        if len(s) < 2:
            return s

        transformed = "^#" + "#".join(s) + "#$"
        radius = [0] * len(transformed)
        center = 0
        right = 0
        best_center = 0
        best_radius = 0

        for i in range(1, len(transformed) - 1):
            mirror = 2 * center - i
            if i < right:
                radius[i] = min(right - i, radius[mirror])
            while transformed[i + radius[i] + 1] == transformed[i - radius[i] - 1]:
                radius[i] += 1
            if i + radius[i] > right:
                center = i
                right = i + radius[i]
            if radius[i] > best_radius:
                best_radius = radius[i]
                best_center = i

        start = (best_center - best_radius) // 2
        return s[start : start + best_radius]
