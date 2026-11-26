from typing import List, Optional


class Solution:
    def inorderSuccessor(self, root: Optional[TreeNode], p: Optional[TreeNode]) -> Optional[TreeNode]:
        nodes: List[TreeNode] = []

        def inorder(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            inorder(node.left)
            nodes.append(node)
            inorder(node.right)

        inorder(root)
        for index in range(len(nodes) - 1):
            if nodes[index] is p:
                return nodes[index + 1]
        return None
