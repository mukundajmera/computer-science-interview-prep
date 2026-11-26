class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        best = 0
        for start in range(len(s)):
            seen = set()
            for end in range(start, len(s)):
                ch = s[end]
                if ch in seen:
                    break
                seen.add(ch)
                best = max(best, end - start + 1)
        return best
