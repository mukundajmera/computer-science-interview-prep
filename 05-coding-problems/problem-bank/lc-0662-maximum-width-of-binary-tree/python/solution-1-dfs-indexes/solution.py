from typing import Dict, Optional


class Solution:
    def widthOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        first_at_depth: Dict[int, int] = {}

        def dfs(node: Optional[TreeNode], depth: int, index: int) -> int:
            if node is None:
                return 0
            first_at_depth.setdefault(depth, index)
            current = index - first_at_depth[depth] + 1
            return max(current, dfs(node.left, depth + 1, index * 2), dfs(node.right, depth + 1, index * 2 + 1))

        return dfs(root, 0, 0)
