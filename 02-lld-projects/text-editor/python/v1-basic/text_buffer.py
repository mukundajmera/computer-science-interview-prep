from abc import ABC, abstractmethod
from typing import List, Optional

class TextBuffer(ABC):
    @abstractmethod
    def insert(self, line_num: int, text: str) -> None:
        pass

    @abstractmethod
    def delete(self, line_num: int) -> Optional[str]:
        pass

    @abstractmethod
    def delete_range(self, start: int, end: int) -> List[str]:
        pass

    @abstractmethod
    def get_line(self, line_num: int) -> Optional[str]:
        pass

    @abstractmethod
    def get_range(self, start: int, end: int) -> List[str]:
        pass

    @abstractmethod
    def get_all(self) -> List[str]:
        pass

class LineBuffer(TextBuffer):
    def __init__(self):
        self._lines: List[str] = []

    def insert(self, line_num: int, text: str) -> None:
        index = max(0, line_num - 1)
        if index >= len(self._lines):
            # Pad with empty strings
            self._lines.extend([""] * (index - len(self._lines)))
            self._lines.append(text)
        else:
            self._lines.insert(index, text)

    def delete(self, line_num: int) -> Optional[str]:
        index = line_num - 1
        if 0 <= index < len(self._lines):
            return self._lines.pop(index)
        return None

    def delete_range(self, start: int, end: int) -> List[str]:
        start_index = max(0, start - 1)
        end_index = min(len(self._lines) - 1, end - 1)
        
        deleted_lines = []
        if start_index <= end_index and start_index < len(self._lines):
            # Pop elements from start_index backwards from end
            for _ in range(end_index - start_index + 1):
                deleted_lines.append(self._lines.pop(start_index))
        return deleted_lines

    def get_line(self, line_num: int) -> Optional[str]:
        index = line_num - 1
        if 0 <= index < len(self._lines):
            return self._lines[index]
        return None

    def get_range(self, start: int, end: int) -> List[str]:
        start_index = max(0, start - 1)
        end_index = min(len(self._lines) - 1, end - 1)
        
        if start_index <= end_index and start_index < len(self._lines):
            return self._lines[start_index:end_index + 1]
        return []

    def get_all(self) -> List[str]:
        return list(self._lines)
