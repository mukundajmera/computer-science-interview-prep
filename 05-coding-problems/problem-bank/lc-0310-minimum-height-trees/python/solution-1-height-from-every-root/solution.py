from collections import deque
from typing import List


class Solution:
    def findMinHeightTrees(self, n: int, edges: List[List[int]]) -> List[int]:
        graph = [[] for _ in range(n)]
        for left, right in edges:
            graph[left].append(right)
            graph[right].append(left)

        def height(root: int) -> int:
            queue = deque([root])
            seen = {root}
            levels = -1
            while queue:
                levels += 1
                for _ in range(len(queue)):
                    node = queue.popleft()
                    for neighbor in graph[node]:
                        if neighbor not in seen:
                            seen.add(neighbor)
                            queue.append(neighbor)
            return levels

        best = min(height(root) for root in range(n))
        return [root for root in range(n) if height(root) == best]
