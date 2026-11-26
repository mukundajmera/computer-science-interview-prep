import heapq
from typing import List


class Solution:
    def findMaximizedCapital(self, k: int, w: int, profits: List[int], capital: List[int]) -> int:
        projects = sorted(zip(capital, profits))
        heap: List[int] = []
        current = w
        index = 0
        for _ in range(k):
            while index < len(projects) and projects[index][0] <= current:
                heapq.heappush(heap, -projects[index][1])
                index += 1
            if not heap:
                break
            current -= heapq.heappop(heap)
        return current
