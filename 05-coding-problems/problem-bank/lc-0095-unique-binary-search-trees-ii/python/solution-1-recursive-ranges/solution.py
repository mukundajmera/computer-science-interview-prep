from typing import List, Optional
class Solution:
    def generateTrees(self, n: int) -> List[Optional[TreeNode]]:
        if n == 0:
            return []
        def build(left: int, right: int) -> List[Optional[TreeNode]]:
            if left > right:
                return [None]
            result = []
            for root_value in range(left, right + 1):
                for left_tree in build(left, root_value - 1):
                    for right_tree in build(root_value + 1, right):
                        result.append(TreeNode(root_value, left_tree, right_tree))
            return result
        return build(1, n)
