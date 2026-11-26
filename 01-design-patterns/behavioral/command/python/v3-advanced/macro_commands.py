"""
Command Pattern - V3 Advanced: Transactional Macro Commands

Demonstrates composing many commands into one command with rollback behavior.
"""
from abc import ABC, abstractmethod
from typing import Iterable, List


class MacroAction(ABC):
    """Command interface for macro steps."""

    @abstractmethod
    def execute(self) -> None:
        """Run the command."""

    @abstractmethod
    def undo(self) -> None:
        """Reverse the command."""


class TextDocument:
    """Receiver used by the macro commands."""

    def __init__(self):
        self._lines: List[str] = []

    @property
    def content(self) -> str:
        return "\n".join(self._lines)

    def append_line(self, line: str) -> int:
        self._lines.append(line)
        return len(self._lines) - 1

    def remove_line(self, index: int) -> str:
        return self._lines.pop(index)

    def replace(self, old: str, new: str) -> None:
        self._lines = [line.replace(old, new) for line in self._lines]


class AppendLineCommand(MacroAction):
    """Command that appends one document line."""

    def __init__(self, document: TextDocument, line: str):
        self._document = document
        self._line = line
        self._index = -1

    def execute(self) -> None:
        self._index = self._document.append_line(self._line)

    def undo(self) -> None:
        if self._index >= 0:
            self._document.remove_line(self._index)
            self._index = -1


class ReplaceTextCommand(MacroAction):
    """Command that replaces text and keeps a before snapshot."""

    def __init__(self, document: TextDocument, old: str, new: str):
        self._document = document
        self._old = old
        self._new = new
        self._before = ""

    def execute(self) -> None:
        self._before = self._document.content
        self._document.replace(self._old, self._new)

    def undo(self) -> None:
        self._document._lines = self._before.split("\n") if self._before else []


class FailingCommand(MacroAction):
    """Test/demo command that simulates a failed external operation."""

    def __init__(self, message: str):
        self._message = message

    def execute(self) -> None:
        raise RuntimeError(self._message)

    def undo(self) -> None:
        return None


class MacroCommand(MacroAction):
    """Composite command that rolls back completed steps on failure."""

    def __init__(self, name: str, commands: Iterable[MacroAction]):
        self.name = name
        self._commands = list(commands)
        self._executed: List[MacroAction] = []

    def execute(self) -> None:
        self._executed = []
        try:
            for command in self._commands:
                command.execute()
                self._executed.append(command)
        except Exception:
            self.undo()
            raise

    def undo(self) -> None:
        for command in reversed(self._executed):
            command.undo()
        self._executed = []


if __name__ == "__main__":
    document = TextDocument()
    macro = MacroCommand(
        "publish draft",
        [
            AppendLineCommand(document, "title"),
            AppendLineCommand(document, "body"),
            ReplaceTextCommand(document, "body", "final body"),
        ],
    )

    macro.execute()
    print(document.content)
    macro.undo()
    print(f"After undo: {document.content!r}")
