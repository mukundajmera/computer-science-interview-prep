from collections import Counter
import heapq
from typing import List


class _WordRank:
    def __init__(self, word: str, count: int) -> None:
        self.word = word
        self.count = count

    def __lt__(self, other: "_WordRank") -> bool:
        if self.count != other.count:
            return self.count < other.count
        return self.word > other.word


class Solution:
    def topKFrequent(self, words: List[str], k: int) -> List[str]:
        counts = Counter(words)
        heap: List[_WordRank] = []
        for word, count in counts.items():
            heapq.heappush(heap, _WordRank(word, count))
            if len(heap) > k:
                heapq.heappop(heap)
        return [
            item.word
            for item in sorted(heap, key=lambda item: (-item.count, item.word))
        ]
