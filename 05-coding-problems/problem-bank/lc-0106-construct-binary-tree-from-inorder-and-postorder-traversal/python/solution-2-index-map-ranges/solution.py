from typing import List, Optional


class Solution:
    def buildTree(self, inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
        index = {value: i for i, value in enumerate(inorder)}

        def build(in_left: int, in_right: int, post_left: int, post_right: int) -> Optional[TreeNode]:
            if in_left > in_right:
                return None
            root_value = postorder[post_right]
            root_index = index[root_value]
            left_size = root_index - in_left
            root = TreeNode(root_value)
            root.left = build(in_left, root_index - 1, post_left, post_left + left_size - 1)
            root.right = build(root_index + 1, in_right, post_left + left_size, post_right - 1)
            return root

        return build(0, len(inorder) - 1, 0, len(postorder) - 1)
