from typing import List, Optional


class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> List[List[int]]:
        result: List[List[int]] = []

        def dfs(node: Optional[TreeNode], remaining: int, path: List[int]) -> None:
            if node is None:
                return
            next_path = path + [node.val]
            if node.left is None and node.right is None and remaining == node.val:
                result.append(next_path)
                return
            dfs(node.left, remaining - node.val, next_path)
            dfs(node.right, remaining - node.val, next_path)

        dfs(root, targetSum, [])
        return result
