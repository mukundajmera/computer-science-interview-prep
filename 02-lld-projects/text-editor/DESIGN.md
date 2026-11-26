# Text Editor - Design

## Cross-links
* [Problem Statement](PROBLEM.md)
* [Approach](APPROACH.md)
* [Rubric](RUBRIC.md)
* [Pitfalls](PITFALLS.md)
* [Follow-ups](FOLLOW-UPS.md)

## System Architecture

The architecture relies on the Command Pattern to separate the editor logic from action execution and reversal.

```mermaid
classDiagram
    class TextEditor {
        -TextBuffer buffer
        -Clipboard clipboard
        -HistoryManager historyManager
        +insert(lineNum, text)
        +delete(lineNum)
        +deleteRange(start, end)
        +copy(start, end)
        +paste(lineNum)
        +display()
        +displayRange(start, end)
        +undo()
        +redo()
    }

    class TextBuffer {
        <<interface>>
        +insert(lineNum, text)
        +delete(lineNum) String
        +deleteRange(start, end) List~String~
        +getLine(lineNum) String
        +getRange(start, end) List~String~
        +getAll() List~String~
    }

    class LineBuffer {
        -List~String~ lines
    }

    class Clipboard {
        -List~String~ content
        +setContent(content)
        +getContent() List~String~
    }

    class HistoryManager {
        -Stack~EditorCommand~ undoStack
        -Stack~EditorCommand~ redoStack
        +execute(Command)
        +undo()
        +redo()
    }

    class EditorCommand {
        <<interface>>
        +execute()
        +undo()
    }

    TextBuffer <|.. LineBuffer
    TextEditor --> TextBuffer
    TextEditor --> Clipboard
    TextEditor --> HistoryManager
    HistoryManager o-- EditorCommand
```

## Sequence Diagram: Editing and Undo

```mermaid
sequenceDiagram
    actor User
    participant Editor as TextEditor
    participant Hist as HistoryManager
    participant Cmd as InsertLineCommand
    participant Buf as LineBuffer

    User->>Editor: insert(2, "Hello")
    Editor->>Cmd: new InsertLineCommand(Buf, 2, "Hello")
    Editor->>Hist: execute(Cmd)
    Hist->>Cmd: execute()
    Cmd->>Buf: insert(2, "Hello")
    Hist->>Hist: push to undoStack
    Hist-->>Editor: done
    Editor-->>User: success

    User->>Editor: undo()
    Editor->>Hist: undo()
    Hist->>Hist: pop Cmd from undoStack
    Hist->>Cmd: undo()
    Cmd->>Buf: delete(2)
    Hist->>Hist: push to redoStack
    Hist-->>Editor: done
    Editor-->>User: undone
```

## Storage Tradeoffs
- A `List<String>` representation (LineBuffer) means inserting at the beginning of a 10,000-line file takes O(N) list shifts. However, standard Python/Java lists are dynamically sized arrays, making shifts relatively fast via memmove.
- For massive files, a LinkedList might seem better for O(1) insertions, but fetching line N takes O(N). A Balanced Tree (Rope) is optimal for large-scale production editors.
