from typing import List, Optional


class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        index = {value: i for i, value in enumerate(inorder)}

        def build(pre_left: int, pre_right: int, in_left: int, in_right: int) -> Optional[TreeNode]:
            if pre_left > pre_right:
                return None
            root_value = preorder[pre_left]
            root_index = index[root_value]
            left_size = root_index - in_left
            root = TreeNode(root_value)
            root.left = build(pre_left + 1, pre_left + left_size, in_left, root_index - 1)
            root.right = build(pre_left + left_size + 1, pre_right, root_index + 1, in_right)
            return root

        return build(0, len(preorder) - 1, 0, len(inorder) - 1)
