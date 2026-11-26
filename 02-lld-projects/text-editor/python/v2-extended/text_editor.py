from typing import List, Optional
from text_buffer import MementoBuffer, EditorMemento
from history_manager import HistoryManager
from commands import InsertCommand, DeleteCommand, ReplaceCommand, MacroCommand

class TextEditor:
    def __init__(self, history_limit: int = 100):
        self.buffer = MementoBuffer()
        self.history_manager = HistoryManager(limit=history_limit)

    def insert(self, line_num: int, text: str) -> None:
        self.history_manager.execute(InsertCommand(self.buffer, line_num, text))

    def delete(self, line_num: int) -> None:
        self.history_manager.execute(DeleteCommand(self.buffer, line_num))
        
    def replace(self, line_num: int, text: str) -> None:
        self.history_manager.execute(ReplaceCommand(self.buffer, line_num, text))

    def get_all_lines(self) -> List[str]:
        return self.buffer.get_all()

    def undo(self) -> None:
        self.history_manager.undo()

    def redo(self) -> None:
        self.history_manager.redo()
        
    def start_macro(self) -> None:
        self.history_manager.start_recording()
        
    def stop_macro(self) -> Optional[MacroCommand]:
        return self.history_manager.stop_recording()
        
    def execute_macro(self, macro: MacroCommand) -> None:
        if macro:
            self.history_manager.execute(macro)
