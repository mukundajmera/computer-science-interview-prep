# Unix POSIX Virtual File System (VFS) - Design

## Version Progression

The project progresses through three distinct evolutionary versions, isolating core logic from advanced OS mechanics:

- **`v1-basic`**: Implements single-thread, in-memory baseline core functionality. Introduces the Inode struct, hierarchy management (directories mapping strings to IDs), basic file creation, and unstructured read/write/seek paths.
- **`v2-extended`**: Adds POSIX access abstraction. Introduces UNIX permissions, independent `FileDescriptor` cursors, open file table management, and soft (symbolic) link cycle detection. 
- **`v3-optimized`**: Introduces storage efficiency and reference semantics. Introduces an inode allocation bitmap, buffer page caching, and hard link reference counting ensuring correct allocation/deallocation on unlink.

## Architecture

The Virtual File System is structured around an object-oriented representation of classical Unix primitives. 

### Data Models
- **`FileType` Enum**: Distinguishes between `FILE`, `DIRECTORY`, and `SYMLINK`.
- **`Inode` Class**: Represents the metadata and data of a file. It doesn't know its own name, only its ID. It contains properties such as `permissions`, `linkCount`, `data` (byte array), `symlinkTarget` (string), and `directoryEntries` (map of string to int).
- **`FileDescriptor` Class**: Represents an open file instance with an independent cursor.

### File System Interface (`VFS`)
Provides POSIX-like system calls:
- `stat(path)`: Returns the Inode.
- `mkdir(path, mode)`: Creates a directory Inode.
- `create(path, mode)`: Creates a file Inode.
- `link(oldPath, newPath)`: Creates a hard link.
- `symlink(target, linkPath)`: Creates a symbolic link.
- `unlink(path)`: Removes a link, potentially deleting the file.
- `open(path, mode)`: Returns a `FileDescriptor`.
- `read(fd, size)`: Reads bytes from the cursor.
- `write(fd, data)`: Writes bytes to the cursor.
- `lseek(fd, offset, whence)`: Moves the cursor.
- `chmod(path, mode)`: Changes permissions.

## Complexity
- **Time Complexity**: Path resolution takes `O(P)` where `P` is the number of components in the path (ignoring symlink restarts which are bounded to 40). `read` and `write` take `O(N)` where `N` is the number of bytes processed.
- **Space Complexity**: `O(N)` where `N` is the total size of file data and directory structures across all Inodes in memory.

## Requirement-to-Section Review

- **Normal use-case**: Addressed in `File System Interface (VFS)` via file creation, path traversal, read, write.
- **Empty/invalid input**: Validation managed in path resolution within VFS interface constraints.
- **Duplicate operation**: Covered by conflict detection (e.g. existing dirent check) implicitly in directory operations.
- **Capacity boundary**: Managed via symbolic link depth limits (`symlinkCount > 40`).
- **Failure rollback**: Demonstrated via link decrement mechanics and bitmap reversion on file unlinking in `v3-optimized`.
- **Public APIs and version-specific feature deltas**: Documented in `Version Progression`.

## Cross-Links
- [Problem Statement](./PROBLEM.md)
- [Code Walkthrough](./CODE-WALKTHROUGH.md)
- [Follow-Ups](./FOLLOW-UPS.md)
- [Pitfalls](./PITFALLS.md)
- [Interview Scoring Rubric](./RUBRIC.md)
