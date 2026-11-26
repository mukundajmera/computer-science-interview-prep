# Strong Answer: Unix Virtual File System (VFS)

**Pacing Target:** 45 minutes

## 1. Introduction & Clarifications (0-5 minutes)

**Say:** "To design the Unix Virtual File System (VFS), I will model the core domain entities—Inodes, Directories, and File Descriptors—based strictly on POSIX semantics. We will build a single-node, in-memory implementation focusing on correctness, path resolution, and reference counting. While our initial design operates in memory, the data structures and boundary contracts are explicitly designed to mirror the interactions one would have with a persistent block device."

By establishing these boundaries early, you frame the discussion around concrete structures rather than distributed systems buzzwords. The primary goal is demonstrating an accurate understanding of how Unix separates filenames from file data and handles hard links versus symbolic links.

## 2. Entity Modeling & APIs (5-15 minutes)

**Say:** "Let's define the core entities and APIs. 
- **`Inode`**: The central entity representing a file or directory. It stores `inodeId`, `fileType` (FILE, DIRECTORY, SYMLINK), `permissions`, `linkCount`, and the actual `data` payload (or `directoryEntries` map). Notably, an `Inode` does not store its own name.
- **`FileDescriptor`**: Returned when opening a file. It tracks the independent `offset` (cursor), the `mode` (read/write/append), and holds a direct reference to the underlying `Inode`.
- **`VFS` (Controller)**: Maintains the global `inodes` map and the root inode. It exposes POSIX system calls like `mkdir`, `create`, `link`, `symlink`, `unlink`, `open`, `read`, `write`, `lseek`, `stat`, and `chmod`."

By strictly adhering to these entities, you show how state is compartmentalized. The `inodes` table acts as our central registry, mimicking a real file system's inode table on disk.

## 3. Design Alternatives & Trade-offs (15-25 minutes)

**Say:** "The most critical design decision is how we represent directories. Rather than nesting `Inode` objects directly inside one another, a directory `Inode` simply contains a map of string names to integer `inodeId`s. This indirection is crucial for supporting **Hard Links**. If two different directories contain a file with the same `inodeId`, they point to the exact same metadata and data. This wouldn't be possible with direct nesting."

**Say:** "Another major trade-off is in path resolution. Our `resolvePath` method splits the input path by `/` and iteratively walks the directory tree. When encountering a `SYMLINK`, we must restart or modify our path resolution. To prevent infinite loops (e.g., `A -> B` and `B -> A`), we must enforce a hard limit on symlink traversals per operation, such as a `MAX_SYMLINKS` constant of 40. This matches real Unix behavior."

## 4. Correctness & Complexity (25-35 minutes)

**Say:** "Let's analyze the complexity of our operations.
- **Time Complexity**: Path resolution takes $O(P)$ where $P$ is the number of path segments, bounded by the maximum symlink depth. `read` and `write` operations take $O(N)$ time, where $N$ is the number of bytes processed, due to copying bytes to/from the in-memory array.
- **Space Complexity**: The system requires $O(I + B)$ space, where $I$ is the number of inodes (metadata) and $B$ is the total bytes allocated across all file data payloads."

**Say:** "For correctness, our `link` operation increments the `linkCount` on the target `Inode`. The `unlink` operation removes the directory entry and decrements the `linkCount`. Crucially, the `Inode` itself is only removed from our central `inodes` map when its `linkCount` reaches zero. This guarantees that as long as a hard link exists, the file data remains intact."

## 5. Failure & Concurrency Discussion (35-45 minutes)

**Say:** "While this baseline is a single-threaded in-memory implementation, let's discuss a concrete concurrency issue: what happens if a file is unlinked while a process is actively reading from it via an open `FileDescriptor`?"

**Say:** "In a real Unix system, an inode is kept alive as long as either its link count is greater than zero OR it has active open file descriptors. In our current implementation, when `unlink` drops the link count to 0, it removes the `Inode` from the `inodes` map. However, because our `FileDescriptor` holds a direct object reference to the `Inode`, the programming language's garbage collector (in Java/Python) will keep the `Inode` alive as long as the `FileDescriptor` exists in memory. This means active reads/writes will still succeed—which actually correctly mimics POSIX semantics where unlinked but open files remain usable! To make this robust in a non-GC environment (like C) or to track it explicitly, we would add an `openHandlesCount` to the `Inode` and only free the memory when `linkCount == 0 && openHandlesCount == 0`."
