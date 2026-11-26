from typing import List
from text_buffer import LineBuffer, TextBuffer
from clipboard import Clipboard
from history_manager import HistoryManager
from commands import InsertLineCommand, DeleteLineCommand, DeleteRangeCommand, PasteCommand

class TextEditor:
    def __init__(self):
        self.buffer: TextBuffer = LineBuffer()
        self.clipboard = Clipboard()
        self.history_manager = HistoryManager()

    def insert(self, line_num: int, text: str) -> None:
        self.history_manager.execute(InsertLineCommand(self.buffer, line_num, text))

    def delete(self, line_num: int) -> None:
        self.history_manager.execute(DeleteLineCommand(self.buffer, line_num))

    def delete_range(self, start: int, end: int) -> None:
        self.history_manager.execute(DeleteRangeCommand(self.buffer, start, end))

    def copy(self, start: int, end: int) -> None:
        self.clipboard.set_content(self.buffer.get_range(start, end))

    def paste(self, line_num: int) -> None:
        content = self.clipboard.get_content()
        if content:
            self.history_manager.execute(PasteCommand(self.buffer, line_num, content))

    def display(self) -> None:
        lines = self.buffer.get_all()
        for i, line in enumerate(lines):
            print(f"{i + 1}: {line}")

    def display_range(self, start: int, end: int) -> None:
        lines = self.buffer.get_range(start, end)
        current_line = max(1, start)
        for line in lines:
            print(f"{current_line}: {line}")
            current_line += 1
            
    def get_all_lines(self) -> List[str]:
        return self.buffer.get_all()

    def undo(self) -> None:
        self.history_manager.undo()

    def redo(self) -> None:
        self.history_manager.redo()
