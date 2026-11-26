from typing import List


class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        if len(needle) == 0:
            return 0

        lps = self._build_lps(needle)
        matched = 0
        for index, char in enumerate(haystack):
            while matched > 0 and char != needle[matched]:
                matched = lps[matched - 1]
            if char == needle[matched]:
                matched += 1
                if matched == len(needle):
                    return index - len(needle) + 1
        return -1

    def _build_lps(self, pattern: str) -> List[int]:
        lps = [0] * len(pattern)
        length = 0
        for index in range(1, len(pattern)):
            while length > 0 and pattern[index] != pattern[length]:
                length = lps[length - 1]
            if pattern[index] == pattern[length]:
                length += 1
                lps[index] = length
        return lps
