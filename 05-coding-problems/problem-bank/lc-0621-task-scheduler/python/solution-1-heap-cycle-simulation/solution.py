from collections import Counter
from heapq import heapify, heappop, heappush
from typing import List


class Solution:
    def leastInterval(self, tasks: List[str], n: int) -> int:
        heap = [-count for count in Counter(tasks).values()]
        heapify(heap)
        time = 0
        while heap:
            used = []
            slots = n + 1
            while slots and heap:
                remaining = heappop(heap) + 1
                if remaining < 0:
                    used.append(remaining)
                time += 1
                slots -= 1
            for count in used:
                heappush(heap, count)
            if heap:
                time += slots
        return time
