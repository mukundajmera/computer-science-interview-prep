from collections import defaultdict
from typing import List


class FileSystem:
    def __init__(self) -> None:
        self.directories = defaultdict(set)
        self.directories["/"]
        self.files = {}

    def ls(self, path: str) -> List[str]:
        if path in self.files:
            return [path.rsplit("/", 1)[-1]]
        return sorted(self.directories[path])

    def mkdir(self, path: str) -> None:
        self._ensure_dir(path)

    def addContentToFile(self, filePath: str, content: str) -> None:
        parent, name = filePath.rsplit("/", 1)
        parent = parent or "/"
        self._ensure_dir(parent)
        self.directories[parent].add(name)
        self.files[filePath] = self.files.get(filePath, "") + content

    def readContentFromFile(self, filePath: str) -> str:
        return self.files[filePath]

    def _ensure_dir(self, path: str) -> None:
        current = "/"
        self.directories[current]
        for part in [piece for piece in path.split("/") if piece]:
            parent = current
            current = current.rstrip("/") + "/" + part
            self.directories[parent].add(part)
            self.directories[current]
