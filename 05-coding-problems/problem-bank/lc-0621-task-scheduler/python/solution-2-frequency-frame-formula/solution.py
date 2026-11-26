from collections import Counter
from typing import List


class Solution:
    def leastInterval(self, tasks: List[str], n: int) -> int:
        counts = Counter(tasks).values()
        max_frequency = max(counts)
        max_count = sum(1 for count in Counter(tasks).values() if count == max_frequency)
        return max(len(tasks), (max_frequency - 1) * (n + 1) + max_count)
