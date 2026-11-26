class Solution:
    def getMinimumDifference(self, root: Optional[TreeNode]) -> int:
        previous = None
        best = float('inf')

        def inorder(node: Optional[TreeNode]) -> None:
            nonlocal previous, best
            if node is None:
                return
            inorder(node.left)
            if previous is not None:
                best = min(best, node.val - previous)
            previous = node.val
            inorder(node.right)

        inorder(root)
        return int(best)
