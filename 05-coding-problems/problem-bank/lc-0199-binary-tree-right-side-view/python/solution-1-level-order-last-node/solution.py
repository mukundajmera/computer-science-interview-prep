from collections import deque

class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        if root is None:
            return []
        view = []
        queue = deque([root])
        while queue:
            level_size = len(queue)
            for index in range(level_size):
                node = queue.popleft()
                if index == level_size - 1:
                    view.append(node.val)
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)
        return view
