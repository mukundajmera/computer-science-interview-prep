"""
Memento Pattern - Text Editor Undo
"""
from dataclasses import dataclass
from typing import Optional, List


# Memento
@dataclass(frozen=True)
class EditorMemento:
    content: str
    cursor_position: int


# Originator
class TextEditor:
    def __init__(self):
        self._content = ""
        self._cursor = 0
    
    def type(self, text: str) -> None:
        self._content = (
            self._content[:self._cursor] + 
            text + 
            self._content[self._cursor:]
        )
        self._cursor += len(text)
    
    def delete(self) -> None:
        if self._cursor > 0:
            self._content = (
                self._content[:self._cursor - 1] + 
                self._content[self._cursor:]
            )
            self._cursor -= 1
    
    def save(self) -> EditorMemento:
        return EditorMemento(self._content, self._cursor)
    
    def restore(self, memento: EditorMemento) -> None:
        self._content = memento.content
        self._cursor = memento.cursor_position
    
    @property
    def content(self) -> str:
        return self._content
    
    def __str__(self) -> str:
        return f'Content: "{self._content}" (cursor at {self._cursor})'


# Caretaker
class History:
    def __init__(self):
        self._undo_stack: List[EditorMemento] = []
        self._redo_stack: List[EditorMemento] = []
    
    def push(self, memento: EditorMemento) -> None:
        self._undo_stack.append(memento)
        self._redo_stack.clear()
    
    def undo(self) -> Optional[EditorMemento]:
        if len(self._undo_stack) > 1:
            self._redo_stack.append(self._undo_stack.pop())
            return self._undo_stack[-1]
        return self._undo_stack[-1] if self._undo_stack else None
    
    def redo(self) -> Optional[EditorMemento]:
        if self._redo_stack:
            memento = self._redo_stack.pop()
            self._undo_stack.append(memento)
            return memento
        return None


if __name__ == "__main__":
    editor = TextEditor()
    history = History()
    
    # Save initial state
    history.push(editor.save())
    
    # Make changes
    editor.type("Hello")
    print(f"After 'Hello': {editor}")
    history.push(editor.save())
    
    editor.type(" World")
    print(f"After ' World': {editor}")
    history.push(editor.save())
    
    editor.type("!")
    print(f"After '!': {editor}")
    history.push(editor.save())
    
    # Undo
    print("\n=== Undo ===")
    memento = history.undo()
    if memento:
        editor.restore(memento)
    print(f"Undo: {editor}")
    
    memento = history.undo()
    if memento:
        editor.restore(memento)
    print(f"Undo: {editor}")
    
    # Redo
    print("\n=== Redo ===")
    memento = history.redo()
    if memento:
        editor.restore(memento)
    print(f"Redo: {editor}")
