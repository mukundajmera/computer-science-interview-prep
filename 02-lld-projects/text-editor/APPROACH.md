# Text Editor - Approach

## Entity Identification
- **Buffer**: To store text. A simple array or list of strings/lines is used for simplicity (LineBuffer). For more advanced features, a gap buffer or piece table could be used.
- **Commands**: Encapsulate actions like insert, delete, and paste.
- **Clipboard**: Holds transient state between a copy and a paste.
- **History Manager**: Controls undo/redo tracking.

## Relationship Mapping
- The `TextEditor` coordinates the `TextBuffer`, `HistoryManager`, and `Clipboard`.
- Mutating actions (Insert, Delete, Paste) instantiate `Command` objects.
- `Command` objects encapsulate the `execute()` and `undo()` logic, modifying the `TextBuffer` when executed or undone.
- The `HistoryManager` maintains stacks of `Command` objects. Executing a new command clears the redo stack and pushes the command to the undo stack.

## Design Pattern Trade-offs
### Command Pattern
- **Pros**: Clean decoupling of what is done from how it is executed and reversed. Perfect fit for undo/redo.
- **Cons**: Every action creates a new object, which can lead to GC overhead if keystrokes are tracked individually rather than line/block level.

### Memento Pattern (Alternative for Undo/Redo)
- **Pros**: Easy to capture state and restore.
- **Cons**: Saving the whole buffer for every small edit is highly inefficient. We chose the Command Pattern to store just the *delta* (e.g., text inserted or text deleted) to be efficient.

## Data Structure Evolution
1. **Simple Array / List of Strings**: Great for line-based editors and simple to implement in a 45-minute interview.
2. **Gap Buffer**: Better for cursor-based text editing, efficiently handling continuous insertions and deletions at a single cursor point.
3. **Piece Table / Rope**: Ideal for massive documents and non-linear edits, reducing contiguous memory moves.
We adopt the **List of Strings (LineBuffer)** for this basic local editor to balance interview time and reasonable line-level operations.

## Complexity Analysis
- **Insert**: O(N) in the worst case (shifting list elements).
- **Delete**: O(N) (shifting list elements).
- **Undo/Redo**: O(1) stack operations, plus the operation complexity.
- **Memory**: O(N + H) where N is buffer size and H is history length.
