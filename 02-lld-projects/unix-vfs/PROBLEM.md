# Unix POSIX Virtual File System (VFS) - Problem Statement

## Problem
Design and implement an in-memory Unix POSIX Virtual File System (VFS) that accurately models core concepts of a POSIX filesystem. The VFS should provide mechanisms for managing files, directories, links, and access.

## Requirements
1. **Inodes & Inode Table**: Represent files and directories using Inodes which store metadata (type, permissions, link count, data size/pointers). The VFS must maintain an Inode table.
2. **Directory Entries (dirent)**: Directories should map names to Inode IDs, conceptually modeling `.`, `..`, and child entries.
3. **Hard Links**: Multiple directory entries can point to the same Inode. An Inode should maintain a reference count (`linkCount`). It is freed only when its reference count drops to 0.
4. **Symbolic Links**: A special file type that stores the target path. Support resolving symbolic links, with cycle detection limiting resolution to a maximum depth (e.g., `MAX_SYMLINKS=40`).
5. **Unix Octal Permissions**: Files and directories must have POSIX-style permissions represented as an octal bitmask (e.g., `0755`).
6. **File Descriptors**: Introduce `FileDescriptor` objects to track independent cursors (seek, read, write offsets) when opening files.

## Deliverables
- A working implementation providing operations like `mkdir`, `create`, `link`, `symlink`, `unlink`, `open`, `read`, `write`, `lseek`, `chmod`, and `stat`.
- Cross-language parity (Java/Python).
- Tests enforcing correct reference counting, symlink cycles, file descriptors cursors, and permissions.
