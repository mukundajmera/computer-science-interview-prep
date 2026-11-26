from typing import List, Optional


class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> List[List[int]]:
        result: List[List[int]] = []
        path: List[int] = []

        def dfs(node: Optional[TreeNode], remaining: int) -> None:
            if node is None:
                return
            path.append(node.val)
            if node.left is None and node.right is None and remaining == node.val:
                result.append(path[:])
            else:
                dfs(node.left, remaining - node.val)
                dfs(node.right, remaining - node.val)
            path.pop()

        dfs(root, targetSum)
        return result
