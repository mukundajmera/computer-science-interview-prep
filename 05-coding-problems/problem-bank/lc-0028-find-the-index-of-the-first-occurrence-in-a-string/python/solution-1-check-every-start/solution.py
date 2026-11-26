class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        n = len(haystack)
        m = len(needle)
        for start in range(n - m + 1):
            offset = 0
            while offset < m and haystack[start + offset] == needle[offset]:
                offset += 1
            if offset == m:
                return start
        return -1
