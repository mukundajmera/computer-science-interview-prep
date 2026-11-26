from typing import Optional


class Solution:
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        return self._serialize(subRoot) in self._serialize(root)

    def _serialize(self, node: Optional[TreeNode]) -> str:
        if node is None:
            return "#,"
        return f"^{node.val}," + self._serialize(node.left) + self._serialize(node.right)
