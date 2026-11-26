class Solution:
    def getMinimumDifference(self, root: Optional[TreeNode]) -> int:
        stack = []
        current = root
        previous = None
        best = float('inf')
        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.left
            current = stack.pop()
            if previous is not None:
                best = min(best, current.val - previous)
            previous = current.val
            current = current.right
        return int(best)
