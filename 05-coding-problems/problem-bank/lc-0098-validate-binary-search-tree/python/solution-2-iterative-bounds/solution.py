class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        stack = [(root, float('-inf'), float('inf'))]
        while stack:
            node, low, high = stack.pop()
            if node is None:
                continue
            if node.val <= low or node.val >= high:
                return False
            stack.append((node.right, node.val, high))
            stack.append((node.left, low, node.val))
        return True
