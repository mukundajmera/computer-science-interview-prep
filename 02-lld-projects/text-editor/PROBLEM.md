# Text Editor - Problem Statement

## Problem Description
Design and implement an in-memory text editor that supports basic operations such as inserting, deleting, copying, pasting text, as well as an undo/redo mechanism. The editor operates on a sequence of lines of text (1-indexed for the user or 0-indexed internally depending on the implementation design, but standard operations typically accept line numbers).

## Functional Requirements
1. **Insert**: Insert a line of text at a given line number.
2. **Delete**: Delete a line of text at a given line number.
3. **DeleteRange**: Delete multiple lines of text between a start and end line number.
4. **Copy**: Copy a range of lines to a clipboard.
5. **Paste**: Paste the copied lines from the clipboard to a specified line number.
6. **Display**: Display all lines of text.
7. **DisplayRange**: Display lines of text within a specified range.
8. **Undo**: Undo the last mutating operation (insert, delete, paste).
9. **Redo**: Redo the last undone operation.

## Non-Functional Requirements
1. **Extensibility**: The system should allow easy additions of new operations.
2. **Correctness**: Edits, copies, and history transitions must be fully correct without losing data.
3. **Memory Efficiency**: History and buffer management should minimize unnecessary string copies.
4. **Performance**: Operations like display and insert should execute reasonably quickly.

## Core Entities
- **TextEditor**: The main interface exposing operations to the user.
- **TextBuffer**: The internal representation of the text being edited.
- **Clipboard**: Holds copied text data for pasting.
- **HistoryManager**: Manages undo and redo stacks.
- **Command**: Represents an operation that can be executed and reversed.

## Constraints
- Everything is in-memory.
- Large files may result in OOM if history is unbounded or full copies are made on each keystroke, so the design should prefer structured line/piece storage or command-pattern reversing over full snapshots.
- Thread safety is not strictly required for this basic local editor, but the design should allow it if needed.
