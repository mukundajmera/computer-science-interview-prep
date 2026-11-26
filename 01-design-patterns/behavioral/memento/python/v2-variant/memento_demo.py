"""
Memento Pattern - V2 Variant: Bounded labeled text editor history.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class EditorMemento:
    """Immutable snapshot of editor state plus caretaker-visible metadata."""

    content: str
    cursor_position: int
    label: str
    created_at: datetime


class TextEditor:
    """Text editor originator that creates and restores mementos."""

    def __init__(self) -> None:
        self._content = ""
        self._cursor = 0

    def type(self, text: str) -> None:
        """Insert text at the current cursor position.

        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        self._content = self._content[:self._cursor] + text + self._content[self._cursor:]
        self._cursor += len(text)

    def delete(self) -> None:
        """Delete one character before the cursor.

        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        if self._cursor > 0:
            self._content = self._content[: self._cursor - 1] + self._content[self._cursor :]
            self._cursor -= 1

    def move_cursor(self, position: int) -> None:
        """Move cursor within document bounds.

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self._cursor = max(0, min(position, len(self._content)))

    def save(self, label: str) -> EditorMemento:
        """Create an immutable editor snapshot.

        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        return EditorMemento(self._content, self._cursor, label, datetime.now())

    def restore(self, memento: EditorMemento) -> None:
        """Restore content and cursor from a memento.

        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        self._content = memento.content
        self._cursor = memento.cursor_position

    @property
    def content(self) -> str:
        return self._content

    def __str__(self) -> str:
        return f'Content: "{self._content}" (cursor at {self._cursor})'


class BoundedHistory:
    """Caretaker that keeps a fixed number of recent editor snapshots."""

    def __init__(self, max_snapshots: int = 10) -> None:
        if max_snapshots < 1:
            raise ValueError("max_snapshots must be positive")
        self._max_snapshots = max_snapshots
        self._undo_stack: List[EditorMemento] = []
        self._redo_stack: List[EditorMemento] = []

    def push(self, memento: EditorMemento) -> None:
        """Store a new snapshot and clear redo history.

        Time Complexity: O(k) when trimming the oldest snapshot
        Space Complexity: O(1) beyond the stored memento
        """
        self._undo_stack.append(memento)
        if len(self._undo_stack) > self._max_snapshots:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> Optional[EditorMemento]:
        """Return the previous snapshot without exposing editor internals.

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if len(self._undo_stack) > 1:
            self._redo_stack.append(self._undo_stack.pop())
            return self._undo_stack[-1]
        return self._undo_stack[-1] if self._undo_stack else None

    def redo(self) -> Optional[EditorMemento]:
        """Return the next snapshot when redo history exists.

        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if not self._redo_stack:
            return None
        memento = self._redo_stack.pop()
        self._undo_stack.append(memento)
        return memento

    def labels(self) -> List[str]:
        """Expose snapshot labels for history UI without exposing state."""
        return [memento.label for memento in self._undo_stack]


if __name__ == "__main__":
    editor = TextEditor()
    history = BoundedHistory(max_snapshots=3)

    history.push(editor.save("empty"))
    editor.type("Hello")
    history.push(editor.save("greeting"))
    editor.type(" World")
    history.push(editor.save("subject"))
    editor.delete()
    history.push(editor.save("trimmed"))

    print("History:", history.labels())
    editor.restore(history.undo())
    print("Undo:", editor)
