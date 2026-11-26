from collections import Counter, defaultdict


class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if not t:
            return ''
        required = Counter(t)
        best = ''
        for start in range(len(s)):
            window = defaultdict(int)
            formed = 0
            for end in range(start, len(s)):
                ch = s[end]
                window[ch] += 1
                if ch in required and window[ch] == required[ch]:
                    formed += 1
                if formed == len(required):
                    candidate = s[start:end + 1]
                    if not best or len(candidate) < len(best):
                        best = candidate
                    break
        return best
