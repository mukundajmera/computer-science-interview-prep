from typing import List
from abc import ABC, abstractmethod

class TextBuffer(ABC):
    @abstractmethod
    def insert(self, line_num: int, text: str) -> None:
        pass

    @abstractmethod
    def delete(self, line_num: int) -> None:
        pass

    @abstractmethod
    def replace(self, line_num: int, text: str) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[str]:
        pass

class LineBuffer(TextBuffer):
    def __init__(self):
        self._lines: List[str] = []

    def insert(self, line_num: int, text: str) -> None:
        # 1-indexed for the user
        index = line_num - 1
        if 0 <= index <= len(self._lines):
            self._lines.insert(index, text)
        else:
            # Append if out of bounds (simplification for testing)
            self._lines.append(text)

    def delete(self, line_num: int) -> None:
        index = line_num - 1
        if 0 <= index < len(self._lines):
            self._lines.pop(index)

    def replace(self, line_num: int, text: str) -> None:
        index = line_num - 1
        if 0 <= index < len(self._lines):
            self._lines[index] = text

    def get_all(self) -> List[str]:
        return list(self._lines)

class EditorMemento:
    def __init__(self, state: List[str]):
        self.state = state
        
class MementoBuffer(TextBuffer):
    def __init__(self):
        self.buffer = LineBuffer()
        
    def insert(self, line_num: int, text: str) -> None:
        self.buffer.insert(line_num, text)
        
    def delete(self, line_num: int) -> None:
        self.buffer.delete(line_num)
        
    def replace(self, line_num: int, text: str) -> None:
        self.buffer.replace(line_num, text)
        
    def get_all(self) -> List[str]:
        return self.buffer.get_all()
        
    def save(self) -> EditorMemento:
        return EditorMemento(self.get_all())
        
    def restore(self, memento: EditorMemento) -> None:
        self.buffer = LineBuffer()
        for i, line in enumerate(memento.state):
            self.buffer.insert(i + 1, line)
