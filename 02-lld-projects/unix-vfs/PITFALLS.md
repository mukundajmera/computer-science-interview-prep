# Unix POSIX Virtual File System (VFS) - Common Pitfalls

## 1. Conflating File Identity and File Name
- **Signal**: The candidate stores the `name` or `path` directly inside the `File` or `Inode` object.
- **Root Cause**: Misunderstanding Unix file semantics where a file is merely a blob of data and metadata (Inode), and its "name" is just a pointer from a directory.
- **Mitigation**: Introduce a strict `Inode` vs `Directory Entry` model.
- **Validation**: Verify if the system can support Hard Links. If names are in the file object, hard links are impossible to model accurately.

## 2. Infinite Symlink Loops
- **Signal**: Path resolution crashes with a `StackOverflowError` or infinite loop timeout.
- **Root Cause**: Failing to track symlink hops during path traversal. E.g. `A -> B`, `B -> A`.
- **Mitigation**: Introduce a max depth counter (e.g., `symlinkCount`) during the `resolvePath` loop.
- **Validation**: Write tests with circular symlinks and ensure they raise an error rather than hanging.

## 3. Global File Cursors
- **Signal**: A single `offset` integer is stored on the `Inode` itself.
- **Root Cause**: Not understanding that multiple processes/threads can open the same file independently.
- **Mitigation**: Introduce a `FileDescriptor` abstraction that maintains the `offset` and `mode` for a specific session.
- **Validation**: Open the same file twice, read 5 bytes from FD1, and check if FD2 still reads from offset 0.

## Cross-Links
- [Design](./DESIGN.md)
- [Follow-Ups](./FOLLOW-UPS.md)
