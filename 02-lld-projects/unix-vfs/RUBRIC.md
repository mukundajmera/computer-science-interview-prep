# Unix POSIX Virtual File System (VFS) - Interview Scoring Rubric

## Scoring rubric

| Dimension | Weight | Strong signal |
| :--- | :--- | :--- |
| **Data Modeling** | 25% | Clearly separates `Inode` (storage/metadata) from `dirent` (naming/hierarchy) and `FileDescriptor` (session state). |
| **Path Resolution** | 25% | Implements robust path traversal that correctly handles both files and directories, and resolves symbolic links while tracking cycle depth. |
| **Memory Management** | 20% | Accurately models reference counting for hard links, only "freeing" the inode when `linkCount == 0`. |
| **I/O Abstractions** | 20% | Uses `FileDescriptor` cursors effectively to isolate reads and writes from concurrent opens. Implements lseek cleanly. |
| **Code Structure** | 10% | Clean, object-oriented code, good encapsulation of internal maps, and clear API boundaries for the VFS operations. |

## Performance bands

- **Strong Hire**: Implements all POSIX semantics (hard links, symlink cycle detection, FD offsets) cleanly.
- **Hire**: Implements inodes and path traversal but might struggle with symlink cycles or FD isolation.
- **No Hire**: Combines file naming and file data into a single object, failing to support hard links. Fails to implement independent cursors.

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design](./DESIGN.md)
