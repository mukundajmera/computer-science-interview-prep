from typing import Iterator, Optional


class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        tokens = []

        def visit(node: Optional[TreeNode]) -> None:
            if node is None:
                tokens.append("#")
                return
            tokens.append(str(node.val))
            visit(node.left)
            visit(node.right)

        visit(root)
        return ",".join(tokens)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        tokens: Iterator[str] = iter(data.split(","))

        def build() -> Optional[TreeNode]:
            token = next(tokens)
            if token == "#":
                return None
            node = TreeNode(int(token))
            node.left = build()
            node.right = build()
            return node

        return build()
