from __future__ import annotations

from typing import Optional


class Solution:
    def isBalanced(self, root: Optional[TreeNode]) -> bool:
        def height(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            best = 0
            stack = [(node, 1)]
            while stack:
                current, depth = stack.pop()
                best = max(best, depth)
                if current.left is not None:
                    stack.append((current.left, depth + 1))
                if current.right is not None:
                    stack.append((current.right, depth + 1))
            return best

        if root is None:
            return True
        stack = [root]
        while stack:
            node = stack.pop()
            if abs(height(node.left) - height(node.right)) > 1:
                return False
            if node.left is not None:
                stack.append(node.left)
            if node.right is not None:
                stack.append(node.right)
        return True
