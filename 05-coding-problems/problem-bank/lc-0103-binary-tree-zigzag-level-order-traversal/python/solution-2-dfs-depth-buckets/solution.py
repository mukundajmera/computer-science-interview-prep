from collections import deque

class Solution:
    def zigzagLevelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        levels = []

        def dfs(node: Optional[TreeNode], depth: int) -> None:
            if node is None:
                return
            if depth == len(levels):
                levels.append(deque())
            if depth % 2 == 0:
                levels[depth].append(node.val)
            else:
                levels[depth].appendleft(node.val)
            dfs(node.left, depth + 1)
            dfs(node.right, depth + 1)

        dfs(root, 0)
        return [list(level) for level in levels]
