from abc import ABC, abstractmethod
from typing import List, Optional
from text_buffer import MementoBuffer, EditorMemento

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

class InsertCommand(Command):
    def __init__(self, buffer: MementoBuffer, line_num: int, text: str):
        self.buffer = buffer
        self.line_num = line_num
        self.text = text
        self.memento: Optional[EditorMemento] = None

    def execute(self) -> None:
        self.memento = self.buffer.save()
        self.buffer.insert(self.line_num, self.text)

    def undo(self) -> None:
        if self.memento:
            self.buffer.restore(self.memento)

class DeleteCommand(Command):
    def __init__(self, buffer: MementoBuffer, line_num: int):
        self.buffer = buffer
        self.line_num = line_num
        self.memento: Optional[EditorMemento] = None

    def execute(self) -> None:
        self.memento = self.buffer.save()
        self.buffer.delete(self.line_num)

    def undo(self) -> None:
        if self.memento:
            self.buffer.restore(self.memento)

class ReplaceCommand(Command):
    def __init__(self, buffer: MementoBuffer, line_num: int, new_text: str):
        self.buffer = buffer
        self.line_num = line_num
        self.new_text = new_text
        self.memento: Optional[EditorMemento] = None

    def execute(self) -> None:
        self.memento = self.buffer.save()
        self.buffer.replace(self.line_num, self.new_text)

    def undo(self) -> None:
        if self.memento:
            self.buffer.restore(self.memento)

class MacroCommand(Command):
    def __init__(self, commands: List[Command]):
        self.commands = commands

    def execute(self) -> None:
        for command in self.commands:
            command.execute()

    def undo(self) -> None:
        for command in reversed(self.commands):
            command.undo()
