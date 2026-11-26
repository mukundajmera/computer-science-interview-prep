from typing import Optional


class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        through_root = self._height(root.left) + self._height(root.right)
        return max(
            through_root,
            self.diameterOfBinaryTree(root.left),
            self.diameterOfBinaryTree(root.right),
        )

    def _height(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))
