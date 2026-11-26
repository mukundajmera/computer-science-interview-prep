from __future__ import annotations

from typing import Optional


class Solution:
    def lowestCommonAncestor(
        self,
        root: Optional[TreeNode],
        p: Optional[TreeNode],
        q: Optional[TreeNode],
    ) -> Optional[TreeNode]:
        if root is None or root is p or root is q:
            return root

        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        if left is not None and right is not None:
            return root
        return left if left is not None else right
