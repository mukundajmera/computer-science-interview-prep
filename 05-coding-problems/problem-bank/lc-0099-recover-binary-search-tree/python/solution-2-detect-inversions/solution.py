from typing import Optional
class Solution:
    def recoverTree(self, root: Optional[TreeNode]) -> None:
        first = second = previous = None
        def inorder(node: Optional[TreeNode]) -> None:
            nonlocal first, second, previous
            if not node:
                return
            inorder(node.left)
            if previous and previous.val > node.val:
                if first is None:
                    first = previous
                second = node
            previous = node
            inorder(node.right)
        inorder(root)
        if first and second:
            first.val, second.val = second.val, first.val
