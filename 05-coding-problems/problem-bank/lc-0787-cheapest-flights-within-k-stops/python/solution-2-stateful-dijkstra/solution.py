import heapq
from typing import List


class Solution:
    def findCheapestPrice(self, n: int, flights: List[List[int]], src: int, dst: int, k: int) -> int:
        graph = [[] for _ in range(n)]
        for start, end, price in flights:
            graph[start].append((end, price))

        max_edges = k + 1
        best = [[float("inf")] * (max_edges + 1) for _ in range(n)]
        best[src][0] = 0
        heap = [(0, src, 0)]
        while heap:
            cost, city, edges = heapq.heappop(heap)
            if city == dst:
                return cost
            if edges == max_edges or cost != best[city][edges]:
                continue
            for next_city, price in graph[city]:
                next_cost = cost + price
                next_edges = edges + 1
                if next_cost < best[next_city][next_edges]:
                    best[next_city][next_edges] = next_cost
                    heapq.heappush(heap, (next_cost, next_city, next_edges))
        return -1
