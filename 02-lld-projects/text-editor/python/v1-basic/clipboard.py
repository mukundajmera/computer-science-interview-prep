from typing import List

class Clipboard:
    def __init__(self):
        self._content: List[str] = []

    def set_content(self, content: List[str]) -> None:
        self._content = list(content)

    def get_content(self) -> List[str]:
        return list(self._content)
