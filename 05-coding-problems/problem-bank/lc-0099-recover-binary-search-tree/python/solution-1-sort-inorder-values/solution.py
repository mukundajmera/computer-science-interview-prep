from typing import Optional
class Solution:
    def recoverTree(self, root: Optional[TreeNode]) -> None:
        nodes = []
        def inorder(node: Optional[TreeNode]) -> None:
            if not node:
                return
            inorder(node.left)
            nodes.append(node)
            inorder(node.right)
        inorder(root)
        for node, value in zip(nodes, sorted(node.val for node in nodes)):
            node.val = value
