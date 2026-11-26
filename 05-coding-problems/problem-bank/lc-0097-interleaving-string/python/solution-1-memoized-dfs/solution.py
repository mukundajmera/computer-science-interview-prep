from __future__ import annotations


class Solution:
    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
        if len(s1) + len(s2) != len(s3):
            return False

        memo: dict[tuple[int, int], bool] = {}

        def can_form(i: int, j: int) -> bool:
            if i + j == len(s3):
                return True
            if (i, j) in memo:
                return memo[(i, j)]

            target = i + j
            take_first = i < len(s1) and s1[i] == s3[target] and can_form(i + 1, j)
            take_second = j < len(s2) and s2[j] == s3[target] and can_form(i, j + 1)
            memo[(i, j)] = take_first or take_second
            return memo[(i, j)]

        return can_form(0, 0)
