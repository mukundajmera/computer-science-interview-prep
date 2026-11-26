# Text Editor - Common Pitfalls

## 1. God-class Buffer
- **Signal**: The `TextBuffer` class contains logic for `copy()`, `paste()`, and `undo()`.
- **Root Cause**: Failing to recognize that history and clipboards are independent domains from the raw string storage.
- **Mitigation**: Strictly separate `TextBuffer` (just storage), `Clipboard` (cross-instance state), and `HistoryManager` (undo/redo logic).

## 2. Full String Copies on Edit (Memento Pattern Abuse)
- **Signal**: The undo stack stores a complete `List<String>` for every single keystroke or command.
- **Root Cause**: Choosing an easy Memento pattern approach without considering memory scaling.
- **Mitigation**: Use the Command Pattern. Store only the delta (the text that was deleted or inserted) inside the command instance.

## 3. Leaky Command Stacks
- **Signal**: When a user undoes an action, then types a new character, the old redo stack is still accessible, leading to conflicting states if redo is called.
- **Root Cause**: Forgetting to clear the `redoStack` whenever a *new* action is executed.
- **Mitigation**: Ensure `execute()` on `HistoryManager` explicitly calls `redoStack.clear()`.

## 4. 0-vs-1 Indexing Bugs
- **Signal**: `insert(1, "Text")` throws an IndexOutOfBoundsException because the underlying list is empty.
- **Root Cause**: Mixing up the user's 1-indexed line numbers with the internal 0-indexed list, or failing to pad the buffer if inserting beyond the current length.
- **Mitigation**: Pick one convention internally (usually 0-indexed) and translate all user inputs at the boundary. Handle inserts past the end of the buffer gracefully (e.g., append).

## 5. Unbounded History Memory
- **Signal**: A user holding down a key creates millions of commands, leading to OutOfMemoryError.
- **Root Cause**: The undo stack has no maximum capacity.
- **Mitigation**: Implement a capacity limit on the undo stack, dropping the oldest commands when the limit is reached.
