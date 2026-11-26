"""
Memento Pattern - V3 Advanced: Transactional checkpoints for a text editor.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass(frozen=True)
class EditorMemento:
    """Immutable snapshot used for undo history, transactions, and checkpoints."""

    content: str
    cursor_position: int
    label: str
    created_at: datetime


class TransactionalTextEditor:
    """Text editor originator with memento-based save and restore."""

    def __init__(self) -> None:
        self._content = ""
        self._cursor = 0

    def type(self, text: str) -> None:
        """Insert text at the cursor.

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

    def save(self, label: str) -> EditorMemento:
        """Create an immutable snapshot.

        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        return EditorMemento(self._content, self._cursor, label, datetime.now())

    def restore(self, memento: EditorMemento) -> None:
        """Restore editor state from a snapshot.

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


class CheckpointHistory:
    """Caretaker with undo/redo, named checkpoints, and transaction rollback."""

    def __init__(self, editor: TransactionalTextEditor) -> None:
        self._editor = editor
        self._undo_stack: List[EditorMemento] = []
        self._redo_stack: List[EditorMemento] = []
        self._checkpoints: Dict[str, EditorMemento] = {}
        self._active_transaction: Optional[EditorMemento] = None

    def snapshot(self, label: str) -> None:
        """Store the editor's current state as a normal undo snapshot."""
        self._undo_stack.append(self._editor.save(label))
        self._redo_stack.clear()

    def save_checkpoint(self, name: str) -> None:
        """Store a named checkpoint outside the linear undo stack."""
        self._checkpoints[name] = self._editor.save(name)

    def restore_checkpoint(self, name: str) -> None:
        """Restore a named checkpoint and end any in-flight transaction."""
        if name not in self._checkpoints:
            raise KeyError(f"Unknown checkpoint: {name}")
        self._active_transaction = None
        self._editor.restore(self._checkpoints[name])

    def begin_transaction(self, label: str) -> None:
        """Capture the pre-transaction state for rollback."""
        if self._active_transaction is not None:
            raise RuntimeError("transaction already active")
        self._active_transaction = self._editor.save(label)

    def rollback_transaction(self) -> None:
        """Restore the pre-transaction snapshot and discard pending edits."""
        if self._active_transaction is None:
            raise RuntimeError("no active transaction")
        self._editor.restore(self._active_transaction)
        self._active_transaction = None

    def commit_transaction(self, label: str) -> None:
        """Commit pending edits as one undoable snapshot."""
        if self._active_transaction is None:
            raise RuntimeError("no active transaction")
        self._active_transaction = None
        self.snapshot(label)

    def undo(self) -> Optional[EditorMemento]:
        """Restore the previous undo snapshot."""
        if len(self._undo_stack) > 1:
            self._redo_stack.append(self._undo_stack.pop())
            memento = self._undo_stack[-1]
            self._editor.restore(memento)
            return memento
        if self._undo_stack:
            self._editor.restore(self._undo_stack[-1])
            return self._undo_stack[-1]
        return None

    def redo(self) -> Optional[EditorMemento]:
        """Restore the next redo snapshot."""
        if not self._redo_stack:
            return None
        memento = self._redo_stack.pop()
        self._undo_stack.append(memento)
        self._editor.restore(memento)
        return memento


if __name__ == "__main__":
    editor = TransactionalTextEditor()
    history = CheckpointHistory(editor)

    history.snapshot("empty")
    editor.type("Draft")
    history.snapshot("draft")
    history.save_checkpoint("approved-draft")

    history.begin_transaction("risky rewrite")
    editor.type(" unsafe")
    history.rollback_transaction()
    print("Rollback:", editor)

    history.begin_transaction("publish edit")
    editor.type(" v2")
    history.commit_transaction("published")
    print("Commit:", editor)
