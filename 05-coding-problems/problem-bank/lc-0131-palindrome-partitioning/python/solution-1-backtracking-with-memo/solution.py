from typing import List


class Solution:
    def partition(self, s: str) -> List[List[str]]:
        result: List[List[str]] = []
        n = len(s)

        def is_palindrome(sub: str) -> bool:
            return sub == sub[::-1]

        def backtrack(start: int, current: List[str]) -> None:
            if start == n:
                result.append(list(current))
                return

            for end in range(start + 1, n + 1):
                chunk = s[start:end]
                if is_palindrome(chunk):
                    current.append(chunk)
                    backtrack(end, current)
                    current.pop()

        backtrack(0, [])
        return result
