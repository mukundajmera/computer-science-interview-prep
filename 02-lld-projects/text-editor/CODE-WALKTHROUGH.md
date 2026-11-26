# Text Editor - Code Walkthrough

## Buffer Mutation Lifecycle
When a user wants to insert text:
1. `TextEditor.insert(lineNum, text)` is called.
2. The editor creates an `InsertLineCommand`, passing it the reference to the `TextBuffer`, the line number, and the text.
3. The command is sent to `HistoryManager.execute(command)`.
4. The history manager clears its redo stack, executes the command, and pushes it onto the undo stack.
5. Inside `InsertLineCommand.execute()`, it calls `buffer.insert(lineNum, text)`.

## History Stack Mechanics
The `HistoryManager` uses two stacks: `undoStack` and `redoStack`.
- **Executing a new command**: The `redoStack` is entirely cleared. The command executes, then is pushed to the `undoStack`.
- **Undo**: Pops a command from the `undoStack`, calls `command.undo()`, and pushes the command to the `redoStack`.
- **Redo**: Pops a command from the `redoStack`, calls `command.execute()`, and pushes the command to the `undoStack`.

## Class Responsibility Mapping
- `LineBuffer`: Solely responsible for maintaining the state of the text lines and handling array manipulations (shifting lines up/down).
- `InsertLineCommand` / `DeleteLineCommand` / `DeleteRangeCommand` / `PasteCommand`: Each is responsible for knowing exactly how to reverse itself. For example, `DeleteLineCommand` remembers the exact string that was deleted so that its `undo()` method can call `buffer.insert()` with that specific string.
- `HistoryManager`: Ignorant of text formatting or buffer state; solely responsible for the stack state transitions.
