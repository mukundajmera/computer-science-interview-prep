from __future__ import annotations

from collections import deque
from typing import Optional


class Solution:
    def lowestCommonAncestor(
        self,
        root: Optional[TreeNode],
        p: Optional[TreeNode],
        q: Optional[TreeNode],
    ) -> Optional[TreeNode]:
        parent_by_node: dict[TreeNode, Optional[TreeNode]] = {root: None}
        queue: deque[TreeNode] = deque([root])

        while p not in parent_by_node or q not in parent_by_node:
            node = queue.popleft()
            if node.left is not None:
                parent_by_node[node.left] = node
                queue.append(node.left)
            if node.right is not None:
                parent_by_node[node.right] = node
                queue.append(node.right)

        p_ancestors: set[TreeNode] = set()
        current = p
        while current is not None:
            p_ancestors.add(current)
            current = parent_by_node[current]

        current = q
        while current not in p_ancestors:
            current = parent_by_node[current]
        return current
