class Solution:
    def scoreOfString(self, s: str) -> int:
        diffs = [abs(ord(s[index]) - ord(s[index - 1])) for index in range(1, len(s))]
        return sum(diffs)
