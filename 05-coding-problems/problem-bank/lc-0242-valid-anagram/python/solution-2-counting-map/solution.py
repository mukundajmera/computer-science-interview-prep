class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        counts = {}
        for ch in s:
            counts[ch] = counts.get(ch, 0) + 1
        for ch in t:
            remaining = counts.get(ch, 0) - 1
            if remaining < 0:
                return False
            if remaining == 0:
                del counts[ch]
            else:
                counts[ch] = remaining
        return not counts
