from typing import Optional


class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        if root is None:
            return "#"
        tokens = []
        stack = [root]
        while stack:
            node = stack.pop()
            if node is None:
                tokens.append("#")
                continue
            tokens.append(str(node.val))
            stack.append(node.right)
            stack.append(node.left)
        return ",".join(tokens)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        tokens = data.split(",")
        index = 0

        def build() -> Optional[TreeNode]:
            nonlocal index
            token = tokens[index]
            index += 1
            if token == "#":
                return None
            node = TreeNode(int(token))
            node.left = build()
            node.right = build()
            return node

        return build()
