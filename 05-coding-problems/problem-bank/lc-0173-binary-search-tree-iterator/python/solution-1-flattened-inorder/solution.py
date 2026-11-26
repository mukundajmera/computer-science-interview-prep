from __future__ import annotations


class BSTIterator:
    def __init__(self, root: Optional[TreeNode]) -> None:
        self.values: list[int] = []
        self.index = 0

        def inorder(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            inorder(node.left)
            self.values.append(node.val)
            inorder(node.right)

        inorder(root)

    def next(self) -> int:
        value = self.values[self.index]
        self.index += 1
        return value

    def hasNext(self) -> bool:
        return self.index < len(self.values)
