class Solution:
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        def mirrors(left: Optional[TreeNode], right: Optional[TreeNode]) -> bool:
            if left is None or right is None:
                return left is right
            return (
                left.val == right.val
                and mirrors(left.left, right.right)
                and mirrors(left.right, right.left)
            )

        return root is None or mirrors(root.left, root.right)
