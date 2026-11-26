class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        stack = []
        current = root
        remaining = k
        while current is not None or stack:
            while current is not None:
                stack.append(current)
                current = current.left
            current = stack.pop()
            remaining -= 1
            if remaining == 0:
                return current.val
            current = current.right
        raise ValueError('k is larger than the tree size')
