from typing import List


class Solution:
    def validTree(self, n: int, edges: List[List[int]]) -> bool:
        if len(edges) != n - 1:
            return False
        parent = list(range(n))
        rank = [0] * n

        def find(value: int) -> int:
            while parent[value] != value:
                parent[value] = parent[parent[value]]
                value = parent[value]
            return value

        for left, right in edges:
            root_left = find(left)
            root_right = find(right)
            if root_left == root_right:
                return False
            if rank[root_left] < rank[root_right]:
                parent[root_left] = root_right
            elif rank[root_left] > rank[root_right]:
                parent[root_right] = root_left
            else:
                parent[root_right] = root_left
                rank[root_left] += 1
        return True
