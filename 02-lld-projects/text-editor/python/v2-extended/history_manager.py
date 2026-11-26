from typing import List, Optional
from commands import Command, MacroCommand

class HistoryManager:
    def __init__(self, limit: int = 100):
        self.limit = limit
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self._is_recording = False
        self._current_macro: List[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        if self._is_recording:
            self._current_macro.append(command)
        else:
            self._undo_stack.append(command)
            if len(self._undo_stack) > self.limit:
                self._undo_stack.pop(0)
            self._redo_stack.clear()

    def undo(self) -> None:
        if self._is_recording:
            return # Don't undo while recording macro
        if self._undo_stack:
            command = self._undo_stack.pop()
            command.undo()
            self._redo_stack.append(command)

    def redo(self) -> None:
        if self._is_recording:
            return
        if self._redo_stack:
            command = self._redo_stack.pop()
            command.execute()
            self._undo_stack.append(command)
            
    def start_recording(self) -> None:
        self._is_recording = True
        self._current_macro = []
        
    def stop_recording(self) -> Optional[MacroCommand]:
        self._is_recording = False
        if not self._current_macro:
            return None
        macro = MacroCommand(self._current_macro)
        self._undo_stack.append(macro)
        if len(self._undo_stack) > self.limit:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        return macro
