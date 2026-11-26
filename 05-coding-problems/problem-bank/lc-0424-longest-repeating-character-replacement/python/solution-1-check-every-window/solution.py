class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        best = 0
        base = ord("A")
        for start in range(len(s)):
            counts = [0] * 26
            max_count = 0
            for end in range(start, len(s)):
                index = ord(s[end]) - base
                counts[index] += 1
                max_count = max(max_count, counts[index])
                length = end - start + 1
                if length - max_count <= k:
                    best = max(best, length)
        return best
