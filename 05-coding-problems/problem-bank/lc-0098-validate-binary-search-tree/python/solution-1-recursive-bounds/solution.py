class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        def is_valid(node: Optional[TreeNode], low: float, high: float) -> bool:
            if node is None:
                return True
            if node.val <= low or node.val >= high:
                return False
            return is_valid(node.left, low, node.val) and is_valid(node.right, node.val, high)

        return is_valid(root, float('-inf'), float('inf'))
