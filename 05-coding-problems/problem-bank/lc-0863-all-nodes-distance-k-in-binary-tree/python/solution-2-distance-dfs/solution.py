from typing import List, Optional


class Solution:
    def distanceK(self, root: Optional[TreeNode], target: Optional[TreeNode], k: int) -> List[int]:
        result: List[int] = []

        def collect(node: Optional[TreeNode], distance: int) -> None:
            if node is None or distance < 0:
                return
            if distance == 0:
                result.append(node.val)
                return
            collect(node.left, distance - 1)
            collect(node.right, distance - 1)

        def distance(node: Optional[TreeNode]) -> int:
            if node is None:
                return -1
            if node is target:
                collect(node, k)
                return 0
            left = distance(node.left)
            if left >= 0:
                if left + 1 == k:
                    result.append(node.val)
                else:
                    collect(node.right, k - left - 2)
                return left + 1
            right = distance(node.right)
            if right >= 0:
                if right + 1 == k:
                    result.append(node.val)
                else:
                    collect(node.left, k - right - 2)
                return right + 1
            return -1

        distance(root)
        return result
