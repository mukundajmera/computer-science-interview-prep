"""
Command Pattern - V2 Variant: Text Editor with Undo/Redo

Each edit is a command object that knows how to execute and undo itself.
"""
from abc import ABC, abstractmethod
from typing import List


class EditorCommand(ABC):
    """Command interface for reversible editor operations."""

    @abstractmethod
    def execute(self) -> None:
        """Apply the command."""

    @abstractmethod
    def undo(self) -> None:
        """Reverse the command."""


class TextEditor:
    """Receiver that owns editable text content."""

    def __init__(self):
        self._content = ""

    @property
    def content(self) -> str:
        return self._content

    def insert(self, index: int, text: str) -> None:
        if index < 0 or index > len(self._content):
            raise ValueError("index out of bounds")
        self._content = self._content[:index] + text + self._content[index:]

    def delete(self, index: int, length: int) -> str:
        if index < 0 or length < 0 or index + length > len(self._content):
            raise ValueError("delete range out of bounds")
        removed = self._content[index:index + length]
        self._content = self._content[:index] + self._content[index + length:]
        return removed


class InsertTextCommand(EditorCommand):
    """Command that inserts text at a fixed position."""

    def __init__(self, editor: TextEditor, text: str, index: int = None):
        self._editor = editor
        self._text = text
        self._index = index
        self._executed_index = 0

    def execute(self) -> None:
        self._executed_index = len(self._editor.content) if self._index is None else self._index
        self._editor.insert(self._executed_index, self._text)

    def undo(self) -> None:
        self._editor.delete(self._executed_index, len(self._text))


class DeleteTextCommand(EditorCommand):
    """Command that deletes and remembers text so undo can restore it."""

    def __init__(self, editor: TextEditor, index: int, length: int):
        self._editor = editor
        self._index = index
        self._length = length
        self._deleted_text = ""

    def execute(self) -> None:
        self._deleted_text = self._editor.delete(self._index, self._length)

    def undo(self) -> None:
        self._editor.insert(self._index, self._deleted_text)


class CommandHistory:
    """Invoker that manages undo and redo stacks."""

    def __init__(self):
        self._undo_stack: List[EditorCommand] = []
        self._redo_stack: List[EditorCommand] = []

    def execute(self, command: EditorCommand) -> None:
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self) -> None:
        if not self._undo_stack:
            return
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self) -> None:
        if not self._redo_stack:
            return
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)


if __name__ == "__main__":
    editor = TextEditor()
    history = CommandHistory()

    history.execute(InsertTextCommand(editor, "hello"))
    history.execute(InsertTextCommand(editor, " world"))
    print(editor.content)

    history.execute(DeleteTextCommand(editor, 5, 6))
    print(editor.content)

    history.undo()
    print(editor.content)
