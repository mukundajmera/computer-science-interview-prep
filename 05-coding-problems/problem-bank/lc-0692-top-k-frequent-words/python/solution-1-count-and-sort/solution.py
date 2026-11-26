from collections import Counter
from typing import List


class Solution:
    def topKFrequent(self, words: List[str], k: int) -> List[str]:
        counts = Counter(words)
        ordered = sorted(counts, key=lambda word: (-counts[word], word))
        return ordered[:k]
