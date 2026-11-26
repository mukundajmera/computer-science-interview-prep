from abc import ABC, abstractmethod
from typing import List, Optional
from text_buffer import TextBuffer

class EditorCommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

class InsertLineCommand(EditorCommand):
    def __init__(self, buffer: TextBuffer, line_num: int, text: str):
        self.buffer = buffer
        self.line_num = line_num
        self.text = text

    def execute(self) -> None:
        self.buffer.insert(self.line_num, self.text)

    def undo(self) -> None:
        self.buffer.delete(self.line_num)

class DeleteLineCommand(EditorCommand):
    def __init__(self, buffer: TextBuffer, line_num: int):
        self.buffer = buffer
        self.line_num = line_num
        self.deleted_text: Optional[str] = None

    def execute(self) -> None:
        self.deleted_text = self.buffer.delete(self.line_num)

    def undo(self) -> None:
        if self.deleted_text is not None:
            self.buffer.insert(self.line_num, self.deleted_text)

class DeleteRangeCommand(EditorCommand):
    def __init__(self, buffer: TextBuffer, start_line: int, end_line: int):
        self.buffer = buffer
        self.start_line = start_line
        self.end_line = end_line
        self.deleted_lines: List[str] = []

    def execute(self) -> None:
        self.deleted_lines = self.buffer.delete_range(self.start_line, self.end_line)

    def undo(self) -> None:
        for i, line in enumerate(self.deleted_lines):
            self.buffer.insert(self.start_line + i, line)

class PasteCommand(EditorCommand):
    def __init__(self, buffer: TextBuffer, line_num: int, content: List[str]):
        self.buffer = buffer
        self.line_num = line_num
        self.content = content

    def execute(self) -> None:
        for i, line in enumerate(self.content):
            self.buffer.insert(self.line_num + i, line)

    def undo(self) -> None:
        if self.content:
            self.buffer.delete_range(self.line_num, self.line_num + len(self.content) - 1)
