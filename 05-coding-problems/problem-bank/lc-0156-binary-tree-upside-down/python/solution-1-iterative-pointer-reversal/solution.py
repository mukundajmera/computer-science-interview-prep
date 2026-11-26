from typing import Optional


class Solution:
    def upsideDownBinaryTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        curr = root
        prev = None
        prev_right = None

        while curr:
            next_node = curr.left
            curr.left = prev_right
            prev_right = curr.right
            curr.right = prev

            prev = curr
            curr = next_node

        return prev
