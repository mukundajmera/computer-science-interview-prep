from collections import deque
from typing import Optional


class Solution:
    def widthOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        queue = deque([(root, 0)])
        best = 0
        while queue:
            level_size = len(queue)
            offset = queue[0][1]
            first = last = 0
            for index in range(level_size):
                node, position = queue.popleft()
                normalized = position - offset
                if index == 0:
                    first = normalized
                if index == level_size - 1:
                    last = normalized
                if node.left:
                    queue.append((node.left, normalized * 2))
                if node.right:
                    queue.append((node.right, normalized * 2 + 1))
            best = max(best, last - first + 1)
        return best
