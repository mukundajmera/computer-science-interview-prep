from collections import Counter
from typing import List


class Solution:
    def findSubstring(self, s: str, words: List[str]) -> List[int]:
        if not words:
            return []
        word_length = len(words[0])
        total_length = word_length * len(words)
        required = Counter(words)
        result: List[int] = []
        for start in range(0, len(s) - total_length + 1):
            seen = Counter()
            used = 0
            while used < len(words):
                begin = start + used * word_length
                piece = s[begin:begin + word_length]
                seen[piece] += 1
                if seen[piece] > required[piece]:
                    break
                used += 1
            if used == len(words):
                result.append(start)
        return result
