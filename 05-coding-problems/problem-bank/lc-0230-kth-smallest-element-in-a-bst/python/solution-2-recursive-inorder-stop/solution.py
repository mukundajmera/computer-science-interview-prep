class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        remaining = k
        answer = None

        def inorder(node: Optional[TreeNode]) -> None:
            nonlocal remaining, answer
            if node is None or answer is not None:
                return
            inorder(node.left)
            if answer is not None:
                return
            remaining -= 1
            if remaining == 0:
                answer = node.val
                return
            inorder(node.right)

        inorder(root)
        if answer is None:
            raise ValueError('k is larger than the tree size')
        return answer
