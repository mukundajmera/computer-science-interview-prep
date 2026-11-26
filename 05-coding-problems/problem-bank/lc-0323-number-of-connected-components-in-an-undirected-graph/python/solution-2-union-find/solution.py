from typing import List


class Solution:
    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        parent = list(range(n))
        rank = [0] * n

        def find(value: int) -> int:
            while parent[value] != value:
                parent[value] = parent[parent[value]]
                value = parent[value]
            return value

        components = n
        for left, right in edges:
            root_left = find(left)
            root_right = find(right)
            if root_left == root_right:
                continue
            if rank[root_left] < rank[root_right]:
                parent[root_left] = root_right
            elif rank[root_left] > rank[root_right]:
                parent[root_right] = root_left
            else:
                parent[root_right] = root_left
                rank[root_left] += 1
            components -= 1
        return components
