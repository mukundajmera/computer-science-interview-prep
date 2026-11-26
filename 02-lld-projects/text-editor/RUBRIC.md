# Text Editor - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | Strong signal |
|-----------|--------|---------------|
| **Domain Modeling** | 25% | Clearly separates the text buffer, the history stacks, and the command objects. Understands the limitations of List vs Rope. |
| **Requirements** | 20% | Successfully implements all required operations (Insert, Delete, Copy, Paste, Undo, Redo). |
| **Correctness** | 25% | Correctly handles 1-indexed (or 0-indexed) boundaries, cleanly deals with edge cases (pasting on an empty buffer, undoing past history). |
| **Extensibility** | 15% | The Command pattern is cleanly applied so that adding a new action (e.g., DeleteRange) requires only a new Command class. |
| **Code Quality** | 15% | Uses appropriate naming, handles invalid line numbers gracefully (exceptions or safe clamps), small focused methods. |

## Performance bands

- **1 - Strong No Hire**: Fails to implement undo/redo. Merges UI, logic, and history into a single God class.
- **2 - No Hire**: Implements undo by saving full copies of the buffer on every edit. Fails basic bounds checking.
- **3 - Leaning Hire**: Implements the Command pattern. Has minor indexing bugs or messy bounds checking. Requires hints to separate history from the buffer.
- **4 - Hire**: Clean Command pattern implementation. Gracefully handles boundary conditions. Good understanding of List vs other buffer structures.
- **5 - Strong Hire**: Excellent separation of concerns. Actively discusses data structure tradeoffs for the buffer (Gap Buffer, Piece Table, Rope) even while implementing the simpler List.

## Cross-links
* [Problem Statement](PROBLEM.md)
* [Design](DESIGN.md)
