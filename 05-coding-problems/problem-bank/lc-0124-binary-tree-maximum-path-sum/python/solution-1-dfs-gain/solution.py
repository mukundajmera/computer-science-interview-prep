from typing import Optional


class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        best = -10**18

        def gain(node: Optional[TreeNode]) -> int:
            nonlocal best
            if node is None:
                return 0
            left = max(0, gain(node.left))
            right = max(0, gain(node.right))
            best = max(best, node.val + left + right)
            return node.val + max(left, right)

        gain(root)
        return best
