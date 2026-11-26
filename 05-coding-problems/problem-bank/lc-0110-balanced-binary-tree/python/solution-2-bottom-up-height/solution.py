from __future__ import annotations

from typing import Optional


class Solution:
    def isBalanced(self, root: Optional[TreeNode]) -> bool:
        if root is None:
            return True
        heights: dict[TreeNode, int] = {}
        stack = [(root, False)]
        while stack:
            node, visited = stack.pop()
            if visited:
                left = heights.get(node.left, 0)
                right = heights.get(node.right, 0)
                if abs(left - right) > 1:
                    return False
                heights[node] = 1 + max(left, right)
                continue
            stack.append((node, True))
            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))
        return True
