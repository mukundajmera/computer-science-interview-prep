from typing import Optional


class Solution:
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        if root is None:
            return subRoot is None
        return (
            self._same_tree(root, subRoot)
            or self.isSubtree(root.left, subRoot)
            or self.isSubtree(root.right, subRoot)
        )

    def _same_tree(self, left: Optional[TreeNode], right: Optional[TreeNode]) -> bool:
        if left is None or right is None:
            return left is right
        return (
            left.val == right.val
            and self._same_tree(left.left, right.left)
            and self._same_tree(left.right, right.right)
        )
