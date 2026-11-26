# Unix POSIX Virtual File System (VFS) - Approach

## Core Components
1. **`Inode`**: The fundamental data structure for a filesystem object. It holds:
    - ID (`inodeId`)
    - Type (`FILE`, `DIRECTORY`, `SYMLINK`)
    - Permissions (`0755`, `0644`)
    - Link Count (`linkCount`)
    - Content (Data bytes for a file, Target path for a symlink, name->inodeId map for a directory)

2. **`VFS` (The Filesystem Controller)**: Maintains the "Inode Table" (a map of ID to `Inode`) and the Root Inode. Handles path parsing to traverse from root to the desired file/directory by successively looking up names in directory `Inode` contents.

3. **`FileDescriptor`**: Returned when opening a file. Contains:
    - A reference to the open `Inode`
    - The access mode (`r`, `w`, etc.)
    - A seek offset (`cursor`), which determines where the next read or write operation will take place. This ensures independent reads from different descriptors.

## Operations
- **Path Resolution**: The heaviest operation. Splits paths by `/`. For each segment, looks up the current directory's entries. If it encounters a symlink, it increments a cycle counter; if the counter exceeds `MAX_SYMLINKS` (40), it throws an error. It then replaces the remaining path with the symlink target and restarts parsing if absolute.
- **Hard Link / Unlink**: `link()` adds a new name to a directory pointing to the same `inodeId` and increments `linkCount`. `unlink()` removes the name and decrements `linkCount`. If 0, the `Inode` is removed from the table.
- **Reading / Writing**: Through `FileDescriptor`, updates the internal buffer of the file's `Inode` and advances the `offset` of the descriptor.

## Cross-Links
- [Problem Statement](./PROBLEM.md)
- [Design](./DESIGN.md)
