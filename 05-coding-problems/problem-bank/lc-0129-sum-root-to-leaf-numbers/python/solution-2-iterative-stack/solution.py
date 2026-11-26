class Solution:
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        total = 0
        stack = [(root, root.val)]
        while stack:
            node, value = stack.pop()
            if node.left is None and node.right is None:
                total += value
            if node.right is not None:
                stack.append((node.right, value * 10 + node.right.val))
            if node.left is not None:
                stack.append((node.left, value * 10 + node.left.val))
        return total
