from __future__ import annotations

from collections import deque


class Solution:
    def averageOfLevels(self, root: Optional[TreeNode]) -> list[float]:
        if root is None:
            return []

        averages = []
        queue = deque([root])
        while queue:
            level_size = len(queue)
            total = 0.0
            for _ in range(level_size):
                node = queue.popleft()
                total += node.val
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)
            averages.append(total / level_size)
        return averages
