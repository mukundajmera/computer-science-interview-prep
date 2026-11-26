from typing import List
from commands import EditorCommand

class HistoryManager:
    def __init__(self):
        self._undo_stack: List[EditorCommand] = []
        self._redo_stack: List[EditorCommand] = []

    def execute(self, command: EditorCommand) -> None:
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self) -> None:
        if self._undo_stack:
            command = self._undo_stack.pop()
            command.undo()
            self._redo_stack.append(command)

    def redo(self) -> None:
        if self._redo_stack:
            command = self._redo_stack.pop()
            command.execute()
            self._undo_stack.append(command)
