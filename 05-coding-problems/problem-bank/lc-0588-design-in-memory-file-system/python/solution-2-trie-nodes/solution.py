from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Node:
    children: Dict[str, "Node"] = field(default_factory=dict)
    content: str = ""
    is_file: bool = False


class FileSystem:
    def __init__(self) -> None:
        self.root = Node()

    def ls(self, path: str) -> List[str]:
        node = self._traverse(path, False)
        if node.is_file:
            return [path.rsplit("/", 1)[-1]]
        return sorted(node.children)

    def mkdir(self, path: str) -> None:
        self._traverse(path, True)

    def addContentToFile(self, filePath: str, content: str) -> None:
        node = self._traverse(filePath, True)
        node.is_file = True
        node.content += content

    def readContentFromFile(self, filePath: str) -> str:
        return self._traverse(filePath, False).content

    def _traverse(self, path: str, create: bool) -> Node:
        node = self.root
        for part in [piece for piece in path.split("/") if piece]:
            if create and part not in node.children:
                node.children[part] = Node()
            node = node.children[part]
        return node
