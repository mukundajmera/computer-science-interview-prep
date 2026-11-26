# Text Editor - Follow-Up Questions

## Follow-up questions
1. **How would you handle a file that is 10GB in size?**
   - Shift from a `LineBuffer` (List of strings) to a `Piece Table` or a `Rope` data structure. Loading the file into memory isn't feasible, so a Piece Table reading via a file pointer, storing only edits in memory, is necessary.

2. **How would you implement continuous typing without creating a command per character?**
   - Implement command merging / debouncing. If the last command on the undo stack is an `InsertTextCommand` occurring at the exact cursor position immediately after the previous one, merge the string rather than pushing a new command.

3. **How would you add syntax highlighting?**
   - Implement a background tokenization service. As the buffer changes, send events (Observer pattern) to the highlighter to re-evaluate the changed lines.

## Variants and extensions
- **Collaborative Editing**: If multiple users are editing the same document over a network. Requires shifting from standard Command patterns to Operational Transformation (OT) or Conflict-free Replicated Data Types (CRDTs).
- **Persistent Disk Checkpointing**: Periodically writing the buffer to disk in the background, recovering from crashes using an append-only transaction log of commands.

## Interviewer probes to prepare
- "If I do `undo()`, `undo()`, then `insert()`, what happens to the two undone commands?"
- "What is the Big-O time complexity of inserting a line at the very beginning of your buffer?"
