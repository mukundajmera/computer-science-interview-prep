# Unix POSIX Virtual File System (VFS) - Follow-Up Questions

## Follow-up questions

1. **How would you implement concurrent access (locking) in this VFS?**
   - **Answer**: Implement read/write locks (e.g., `ReentrantReadWriteLock` in Java, `threading.RLock` in Python) at the `Inode` level. Directory modifications (like `link`, `unlink`) require locking the parent directory's Inode.

2. **How would you handle mounting another filesystem?**
   - **Answer**: Add a `mountPoint` flag or reference in the `Inode` or a global Mount Table. During path resolution, if a directory is a mount point, traverse into the root Inode of the mounted VFS.

3. **How does standard Unix differ from this in-memory model regarding memory exhaustion?**
   - **Answer**: Unix uses a block-based storage model (e.g., 4KB blocks) mapped via direct, indirect, and doubly-indirect pointers. This in-memory model uses contiguous byte arrays, which can fragment memory and cause OutOfMemory errors for large files.

## Variants and extensions
- **Block-Based Storage**: Rewrite the `Inode` data representation to use a list of fixed-size blocks (e.g., `byte[4096]`) rather than a single contiguous array.
- **User and Group Permissions**: Expand the simple octal mask to check against a current `uid` and `gid`.

## Interviewer probes to prepare
- "What happens to the open `FileDescriptor` if I call `unlink` on the file while it is open?" (Standard Unix keeps the file alive until the FD is closed, meaning ref count must also include open FDs).
- "How do you handle `.` and `..` in path resolution?"

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design](./DESIGN.md)
