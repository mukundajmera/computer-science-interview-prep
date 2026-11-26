class Solution:
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        def dfs(node: Optional[TreeNode], prefix: int) -> int:
            if node is None:
                return 0
            value = prefix * 10 + node.val
            if node.left is None and node.right is None:
                return value
            return dfs(node.left, value) + dfs(node.right, value)

        return dfs(root, 0)
