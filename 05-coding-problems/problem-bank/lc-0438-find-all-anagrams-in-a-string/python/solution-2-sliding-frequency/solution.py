from typing import List


class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        window_size = len(p)
        if window_size > len(s):
            return []
        target = [0] * 26
        window = [0] * 26
        base = ord("a")
        for index in range(window_size):
            target[ord(p[index]) - base] += 1
            window[ord(s[index]) - base] += 1
        result: List[int] = []
        if window == target:
            result.append(0)
        for right in range(window_size, len(s)):
            window[ord(s[right]) - base] += 1
            window[ord(s[right - window_size]) - base] -= 1
            if window == target:
                result.append(right - window_size + 1)
        return result
