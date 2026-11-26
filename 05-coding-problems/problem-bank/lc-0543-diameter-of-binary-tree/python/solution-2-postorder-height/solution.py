from typing import Optional


class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        self._best = 0

        def height(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            left = height(node.left)
            right = height(node.right)
            self._best = max(self._best, left + right)
            return 1 + max(left, right)

        height(root)
        return self._best
