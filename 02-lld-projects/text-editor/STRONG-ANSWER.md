# Strong Answer: Text Editor

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the in-memory Text Editor, I will focus on modeling the core entities, defining the operations for text manipulation, and ensuring an efficient undo/redo mechanism. I'll begin by outlining the core data models and APIs, then progress to the design patterns that manage state (Commands/Mementos), and finally address data structure choices for the text buffer itself."

By establishing these constraints early, we frame the discussion around concrete engineering trade-offs. The high-level requirements dictate a system capable of handling inserts, deletes, copy, paste, and undo/redo while maintaining precise state transitions for the text buffer.

## 2. Entity Modeling & APIs (5-15 minutes)

**Say:** "Let's discuss the entity modeling. The core entities I have identified include `TextEditor`, `TextBuffer`, `HistoryManager`, `Clipboard`, and `Command`. The `TextEditor` acts as a facade, coordinating the buffer, clipboard, and history manager."

The public APIs match the merged v1-basic contract:
*   `insert(line_num, text)`: Inserts a line of text at 1-indexed `line_num`.
*   `delete(line_num)`: Deletes a line of text.
*   `delete_range(start, end)`: Deletes multiple lines (inclusive).
*   `copy(start, end)`: Copies lines to the clipboard.
*   `paste(line_num)`: Pastes clipboard contents at `line_num`.
*   `get_all_lines()`: Returns the full buffer state.
*   `undo()` / `redo()`: Manipulates history state.

Empty or invalid inputs (like deleting out of bounds or pasting empty clipboards) are handled gracefully (ignored or safely clamped) without throwing fatal exceptions, matching the `TextBuffer` contract.

## 3. Design Alternatives & Data Structures (15-25 minutes)

**Say:** "For the text representation, we have several design alternatives. The simplest is a `LineBuffer` (List of Strings), which is excellent for line-based editors and easy to implement in 45 minutes. However, as the document grows or we need character-level cursor edits, a `GapBuffer` or `PieceTable` is superior."

*   **LineBuffer (v1/v2):** Uses a standard dynamic array (List). Inserts and deletes are O(N) due to array shifts, but it is highly intuitive.
*   **GapBuffer (v3):** Allocates a fixed-capacity array with a "gap" of empty slots at the cursor location. Edits near the cursor are O(1). When the gap is exhausted, the capacity is doubled (O(N) resize), maintaining amortized O(1) edits.

## 4. History Management & Command Pattern (25-35 minutes)

**Say:** "To implement Undo/Redo efficiently, we avoid saving full snapshots for every keystroke. Instead, I'll use the **Command Pattern**. Each operation (Insert, Delete) is encapsulated into a Command object that knows how to `execute()` and `undo()` itself."

*   **v1-basic (Command Pattern):** An `InsertCommand` stores the line number and text. Its `undo()` simply calls `buffer.delete()`. This is highly memory efficient.
*   **v2-extended (Memento & Macros):** As operations get complex, calculating the reverse can be hard. The v2 approach uses the **Memento Pattern** to save block state snapshots, combined with a `MacroCommand` for batching edits into a single atomic undoable action.

## 5. Failure Rollbacks & Concurrency/Capacity Boundaries (35-45 minutes)

**Say:** "Let's trace a concrete failure scenario: Undo/Redo stack invalidation and capacity boundaries."

**Scenario Trace:**
1.  **Duplicate Operation / State Divergence:** If a user pastes twice, two identical Commands are pushed to the undo stack. We ensure exact referential state by having each command execute against the unified `TextBuffer`.
2.  **Stack Invalidation:** If a user performs actions A and B, undoes B, and then inserts new text C, the redo stack containing B **must** be cleared. The `HistoryManager` enforces this contract: any new `execute()` instantly clears the `_redo_stack`.
3.  **Capacity Boundary (`GapBuffer`):** In v3, when `gap_start == gap_end`, the buffer hits its capacity boundary. A resize allocates a `new_capacity = current_capacity * 2`. If an insert is requested out of bounds, the logical length clamps it to the max valid index (`min(index, logical_length)`), preventing index-out-of-bounds failures.

Thread safety is generally outside the scope of a local, in-memory editor implementation, but if multiple cursors were added (Collaborative Editing), Operational Transformation (OT) or CRDTs would replace the local Command stack.

## 6. Version Deltas Summary

| Version | Features | Buffer Strategy | History Strategy |
|---|---|---|---|
| **v1-basic** | Insert, Delete, Copy, Paste | `LineBuffer` (List) | Command Pattern (Deltas) |
| **v2-extended** | Macros, Replace, History Limits | `MementoBuffer` | Memento + Macro Commands |
| **v3-optimized** | Character/Cursor Edits | `GapBuffer` (Fixed + Resize) | N/A (Focus on Buffer) |
