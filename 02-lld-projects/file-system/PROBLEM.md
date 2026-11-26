# File System

## Problem Statement

Design an in-memory file system that supports creating files and directories, navigating paths, and performing operations like copy, move, and search.

---

## Functional Requirements

1. **File Operations**: Create, read, write, and delete files
2. **Directory Operations**: Create, delete, list contents of directories
3. **Navigation**: Navigate using absolute and relative paths
4. **Move/Copy**: Move and copy files/directories between locations
5. **Search**: Find files by name, extension, or size
6. **Metadata**: Track file size, creation time, modification time
7. **Path Resolution**: Support both absolute (/root/dir/file) and relative paths
8. **Permissions**: Read/write/execute permissions for user/group/others (v3)

---

## Non-Functional Requirements

1. **Thread Safety**: Handle concurrent file operations safely
2. **Performance**: O(1) path component lookup, efficient tree traversal
3. **Scalability**: Support large directory trees (thousands of files)
4. **Consistency**: Prevent conflicts during concurrent modifications
5. **Memory Efficiency**: Optimize storage for large file counts

---

## Constraints & Assumptions

- In-memory file system (no actual disk I/O)
- Single root directory ("/")
- File content stored as strings (simplified)
- Unique names within same directory
- No symbolic links in v1/v2 (added in v3)
- Maximum path depth: 100 levels
- Maximum file size: 1GB (represented as content length)

---

## Sample Interactions

```
1. Create directory: mkdir /home/user/documents
2. Create file: touch /home/user/documents/notes.txt
3. Write to file: write /home/user/documents/notes.txt "Hello World"
4. Read file: cat /home/user/documents/notes.txt → "Hello World"
5. List directory: ls /home/user/documents → [notes.txt]
6. Copy file: cp /home/user/documents/notes.txt /home/user/backup/
7. Move file: mv /home/user/backup/notes.txt /home/user/archive/
8. Search: find /home -name "*.txt" → [/home/user/documents/notes.txt]
9. Delete: rm /home/user/archive/notes.txt
```

---

## Clarifying Questions to Ask

1. "Should we support symbolic and hard links?"
2. "What permission model - Unix-style or simplified?"
3. "Do we need to support file locking?"
4. "Should directory listing be sorted?"
5. "How do we handle circular references in copy/move?"
6. "What's the maximum file/directory name length?"
7. "Should we track access time (last read)?"
8. "Do we need a recycle bin/trash feature?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| FileSystem | Main system, manages root, path resolution |
| FileSystemEntry | Base class for files and directories |
| File | Stores content, size, metadata |
| Directory | Contains children entries, navigation |
| Path | Parse and resolve path strings |
| Permission | Access control (read/write/execute) |
| Metadata | Timestamps, owner, size |

---

## Scoring Rubric

See [RUBRIC.md](./RUBRIC.md).

## Common Pitfalls

See [PITFALLS.md](./PITFALLS.md).

## Follow-up Questions

See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Variants and Extensions

1. Add ACL-based permissions and ownership.
2. Add indexed search for large directory trees.
3. Add symbolic links and cycle-safe traversal.
4. Add snapshot/versioning support for rollback.

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Core File/Directory, create/delete, path navigation |
| v2-extended | Copy/move, search by name/extension/size, metadata |
| v3-optimized | Permissions, symbolic links, thread-safe operations |
