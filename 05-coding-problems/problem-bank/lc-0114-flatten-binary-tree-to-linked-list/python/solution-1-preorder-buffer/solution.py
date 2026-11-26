from __future__ import annotations

from typing import Optional


class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        nodes: list[TreeNode] = []

        def collect_preorder(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            nodes.append(node)
            collect_preorder(node.left)
            collect_preorder(node.right)

        collect_preorder(root)
        for index, node in enumerate(nodes):
            node.left = None
            node.right = nodes[index + 1] if index + 1 < len(nodes) else None
