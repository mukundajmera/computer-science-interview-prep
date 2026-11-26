from typing import Dict, Optional


class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        prefixes: Dict[int, int] = {0: 1}

        def dfs(node: Optional[TreeNode], prefix: int) -> int:
            if node is None:
                return 0
            current = prefix + node.val
            count = prefixes.get(current - targetSum, 0)
            prefixes[current] = prefixes.get(current, 0) + 1
            count += dfs(node.left, current)
            count += dfs(node.right, current)
            prefixes[current] -= 1
            if prefixes[current] == 0:
                del prefixes[current]
            return count

        return dfs(root, 0)
