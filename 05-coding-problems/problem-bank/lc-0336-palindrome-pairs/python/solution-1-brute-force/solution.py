from typing import List


class Solution:
    def palindromePairs(self, words: List[str]) -> List[List[int]]:
        result = []
        for i, first in enumerate(words):
            for j, second in enumerate(words):
                if i != j and self._is_palindrome(first + second):
                    result.append([i, j])
        return result

    def _is_palindrome(self, value: str) -> bool:
        return value == value[::-1]
