from typing import Optional


class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        if root is None:
            return 0
        return (
            self._count_from(root, targetSum)
            + self.pathSum(root.left, targetSum)
            + self.pathSum(root.right, targetSum)
        )

    def _count_from(self, node: Optional[TreeNode], remaining: int) -> int:
        if node is None:
            return 0
        count = 1 if node.val == remaining else 0
        count += self._count_from(node.left, remaining - node.val)
        count += self._count_from(node.right, remaining - node.val)
        return count
