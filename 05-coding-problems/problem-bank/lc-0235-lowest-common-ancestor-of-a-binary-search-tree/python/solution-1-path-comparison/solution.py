from __future__ import annotations

from typing import Optional


class Solution:
    def lowestCommonAncestor(
        self,
        root: Optional[TreeNode],
        p: Optional[TreeNode],
        q: Optional[TreeNode],
    ) -> Optional[TreeNode]:
        if root is None or p is None or q is None:
            return root

        def path_to(target: int) -> list[TreeNode]:
            path: list[TreeNode] = []
            current = root
            while current is not None:
                path.append(current)
                if target < current.val:
                    current = current.left
                elif target > current.val:
                    current = current.right
                else:
                    break
            return path

        p_path = path_to(p.val)
        q_path = path_to(q.val)
        answer = root
        for left, right in zip(p_path, q_path):
            if left is not right:
                break
            answer = left
        return answer
