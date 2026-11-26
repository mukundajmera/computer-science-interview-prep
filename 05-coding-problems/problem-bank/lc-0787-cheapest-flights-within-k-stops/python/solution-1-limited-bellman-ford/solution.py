from typing import List


class Solution:
    def findCheapestPrice(self, n: int, flights: List[List[int]], src: int, dst: int, k: int) -> int:
        inf = 10**12
        previous = [inf] * n
        previous[src] = 0
        answer = previous[dst]
        for _ in range(k + 1):
            current = previous[:]
            for start, end, price in flights:
                if previous[start] != inf:
                    current[end] = min(current[end], previous[start] + price)
            previous = current
            answer = min(answer, previous[dst])
        return -1 if answer == inf else answer
