# Memento Pattern - Theory & Interview Guide

## 📚 Core Concept

The Memento pattern captures and externalizes an object's internal state so that it can be restored later, without violating encapsulation.

### Key Components

1. **Originator**: The object whose state needs to be saved
2. **Memento**: Stores internal state of Originator (immutable)
3. **Caretaker**: Manages Mementos (history), doesn't examine contents

## 🎯 Problem It Solves

**Without Memento:**
```java
// Exposing internal state violates encapsulation
class Editor {
    public String content;  // Now anyone can access/modify!
}

// Saving/restoring requires knowing internals
EditorState save = new EditorState(editor.content, editor.cursor...);
```

**With Memento:**
```java
Memento snapshot = editor.save();     // Editor creates memento
history.push(snapshot);                // Caretaker stores it
editor.restore(history.pop());         // Restore without knowing internals
```

## ✅ When to Use

1. **Undo/Redo functionality**
2. **Snapshots** for rollback
3. **Transactional** operations
4. **State history** for debugging
5. Examples: Text editors, games, database transactions

## 🎤 Interview Q&A

### Q1: How does Memento preserve encapsulation?

**A:** 
- Originator creates the memento (has access to its own state)
- Memento's state is private (or package-private in Java)
- Caretaker only holds mementos, never examines them
- Only Originator can extract state from memento

### Q2: What's the trade-off?

**A:** **Memory consumption!** Each memento stores a snapshot. Mitigation:
- Store only changed data (deltas)
- Limit history size
- Use serialization/compression
- Implement incremental mementos

### Q3: Command vs Memento for undo?

**A:**
| Command | Memento |
|---------|---------|
| Stores how to undo | Stores complete state |
| Less memory (usually) | Full snapshot (more memory) |
| Requires inverse operation | Any operation reversible |
| Complex undo logic | Simple restore |

### Q4: Nested class implementation?

**A:** In Java, Memento is often a static nested class:
```java
public class Editor {
    public static class Memento {
        private final String state;  // Package-private
        private Memento(String state) { this.state = state; }
    }
}
```
This allows Originator access but hides from others.

## 💻 Code Patterns

### Java
```java
class Editor {
    private String content;
    
    public Memento save() {
        return new Memento(content);
    }
    
    public void restore(Memento memento) {
        this.content = memento.getState();
    }
    
    public static class Memento {
        private final String state;
        
        private Memento(String state) {
            this.state = state;
        }
        
        private String getState() {
            return state;
        }
    }
}

class History {
    private Stack<Editor.Memento> history = new Stack<>();
    
    public void save(Editor editor) {
        history.push(editor.save());
    }
    
    public void undo(Editor editor) {
        if (!history.isEmpty()) {
            editor.restore(history.pop());
        }
    }
}
```

### Python
```python
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Memento:
    """Immutable memento storing editor state."""
    content: str
    cursor_pos: int

class Editor:
    def __init__(self):
        self._content = ""
        self._cursor = 0
    
    def save(self) -> Memento:
        return Memento(self._content, self._cursor)
    
    def restore(self, memento: Memento) -> None:
        self._content = memento.content
        self._cursor = memento.cursor_pos

class History:
    def __init__(self):
        self._mementos: List[Memento] = []
    
    def backup(self, editor: Editor) -> None:
        self._mementos.append(editor.save())
    
    def undo(self, editor: Editor) -> None:
        if self._mementos:
            editor.restore(self._mementos.pop())
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Command** | Can use Memento for undo |
| **Iterator** | Memento can store iteration state |
| **Prototype** | Alternative for saving state (clone) |

---

[← Back to Memento](./README.md)
