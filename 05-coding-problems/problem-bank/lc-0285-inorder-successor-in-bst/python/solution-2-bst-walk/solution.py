from typing import Optional


class Solution:
    def inorderSuccessor(self, root: Optional[TreeNode], p: Optional[TreeNode]) -> Optional[TreeNode]:
        successor = None
        current = root
        while current:
            if p.val < current.val:
                successor = current
                current = current.left
            else:
                current = current.right
        return successor
