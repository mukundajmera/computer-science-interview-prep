# Unix POSIX Virtual File System (VFS) - Code Walkthrough

## Version Breakdown (Python & Java)

Both language implementations maintain strict feature parity across all three versions.

### `v1-basic`: Core Functionality & Initialization
When the `VFS` is initialized, it creates an empty `inodes` map. It immediately creates `Inode` #1, marked as a `DIRECTORY`, representing the root directory `/`. The root directory is pre-populated with `.` and `..` entries pointing to itself.
Path traversal handles normal use-cases, and invalid paths correctly return `null`/`None`.

### `v2-extended`: Abstractions & Security
In `v2-extended`, we add UNIX permissions checked via octal properties (e.g. `0755`).
We manage an **open file table** using `FileDescriptor` objects. When `open()` is called, a new `FileDescriptor` is instantiated holding a reference to the `Inode` and an initial independent offset (cursor) of `0`. Duplicate openings of the same file return distinct descriptors, keeping state isolated.
When `read(fd, size)` is called, it slices the `Inode`'s data array from `fd.offset` to `fd.offset + size`, and advances `fd.offset`.
When `lseek(fd, offset, whence)` is called, `whence` dictates if the offset is relative to the start (0), current position (1), or end of the file (2).

### `v3-optimized`: Allocations & Graph Safety
In `v3-optimized`, we implement hard link reference counting and page cache optimizations.
When `link()` is called to create a hard link, it validates against empty/invalid directory constraints and duplicates entries, doing `targetInode.linkCount++`.
To manage failure rollbacks and de-allocations, when `unlink()` is called, we remove the name entry from the parent. We decrement `linkCount`. If it hits 0, `inodes.remove(targetInodeId)` is called, completely freeing the memory and we revert the allocation bit in `inodeBitmap` (our storage bitmap tracker).

### Path Resolution (All Versions)
The `resolvePath` method (in Java) or `_resolve_path` (in Python) is the engine of the filesystem. It splits the given absolute path by `/`.
It traverses directory by directory. If it hits a `SYMLINK` file type:
1. It increments `symlinkCount`. If `> 40`, it throws a RecursionError.
2. It fetches `symlinkTarget`.
3. If absolute (starts with `/`), it resets the current directory to root.
4. It prepends the target's parts to the remaining parts of the original path and continues.

## Cross-Links
- [Design](./DESIGN.md)
