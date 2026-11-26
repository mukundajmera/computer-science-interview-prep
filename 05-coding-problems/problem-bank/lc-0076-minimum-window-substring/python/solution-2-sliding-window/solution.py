from collections import Counter, defaultdict


class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if not t:
            return ''
        required = Counter(t)
        window = defaultdict(int)
        formed = 0
        left = 0
        best_start = 0
        best_length = float('inf')
        for right, ch in enumerate(s):
            window[ch] += 1
            if ch in required and window[ch] == required[ch]:
                formed += 1
            while formed == len(required):
                if right - left + 1 < best_length:
                    best_start = left
                    best_length = right - left + 1
                removed = s[left]
                window[removed] -= 1
                if removed in required and window[removed] < required[removed]:
                    formed -= 1
                left += 1
        if best_length == float('inf'):
            return ''
        return s[best_start:best_start + best_length]
