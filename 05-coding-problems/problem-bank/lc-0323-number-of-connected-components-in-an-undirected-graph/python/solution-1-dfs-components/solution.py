from typing import List


class Solution:
    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        graph = [[] for _ in range(n)]
        for left, right in edges:
            graph[left].append(right)
            graph[right].append(left)
        visited = set()
        components = 0
        for node in range(n):
            if node in visited:
                continue
            components += 1
            stack = [node]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                stack.extend(graph[current])
        return components
