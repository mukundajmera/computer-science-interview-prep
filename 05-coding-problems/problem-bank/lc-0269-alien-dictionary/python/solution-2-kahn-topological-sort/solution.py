import heapq
from collections import defaultdict
from typing import Dict, List, Set


class Solution:
    def alienOrder(self, words: List[str]) -> str:
        graph: Dict[str, Set[str]] = {char: set() for word in words for char in word}
        indegree = {char: 0 for char in graph}
        for first, second in zip(words, words[1:]):
            limit = min(len(first), len(second))
            index = 0
            while index < limit and first[index] == second[index]:
                index += 1
            if index == limit:
                if len(first) > len(second):
                    return ""
            else:
                before, after = first[index], second[index]
                if after not in graph[before]:
                    graph[before].add(after)
                    indegree[after] += 1
        heap = [char for char, degree in indegree.items() if degree == 0]
        heapq.heapify(heap)
        order = []
        while heap:
            char = heapq.heappop(heap)
            order.append(char)
            for nxt in graph[char]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    heapq.heappush(heap, nxt)
        return "".join(order) if len(order) == len(indegree) else ""
