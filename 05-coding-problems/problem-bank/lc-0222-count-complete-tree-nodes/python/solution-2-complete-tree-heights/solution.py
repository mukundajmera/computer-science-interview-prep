class Solution:
    def countNodes(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0
        left_height = self._left_height(root.left)
        right_height = self._left_height(root.right)
        if left_height == right_height:
            return (1 << left_height) + self.countNodes(root.right)
        return (1 << right_height) + self.countNodes(root.left)

    def _left_height(self, node: Optional[TreeNode]) -> int:
        height = 0
        while node is not None:
            height += 1
            node = node.left
        return height
