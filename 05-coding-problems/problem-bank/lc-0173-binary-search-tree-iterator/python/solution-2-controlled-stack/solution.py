from __future__ import annotations


class BSTIterator:
    def __init__(self, root: Optional[TreeNode]) -> None:
        self.stack: list[TreeNode] = []
        self._push_left(root)

    def next(self) -> int:
        node = self.stack.pop()
        self._push_left(node.right)
        return node.val

    def hasNext(self) -> bool:
        return bool(self.stack)

    def _push_left(self, node: Optional[TreeNode]) -> None:
        while node is not None:
            self.stack.append(node)
            node = node.left
