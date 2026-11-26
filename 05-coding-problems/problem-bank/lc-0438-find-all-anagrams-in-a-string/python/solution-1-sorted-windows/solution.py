from typing import List


class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        window_size = len(p)
        if window_size > len(s):
            return []
        target = sorted(p)
        result: List[int] = []
        for start in range(len(s) - window_size + 1):
            if sorted(s[start:start + window_size]) == target:
                result.append(start)
        return result
