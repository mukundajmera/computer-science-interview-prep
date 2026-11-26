# Design Approach for File System

A step-by-step thought process for designing the file system.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| File System | ✅ Yes | Main system container |
| File | ✅ Yes | Stores content data |
| Directory | ✅ Yes | Contains files/directories |
| Path | ✅ Yes | Location identifier |
| Content | ❌ No | Attribute of File |
| Permission | ✅ Yes | Access control (v3) |
| Metadata | ✅ Yes | File/directory properties |

**Final Entities**: FileSystem, FileSystemEntry (abstract), File, Directory, Path, Permission, Metadata

---

## Step 2: Define Relationships

```
FileSystem (1) ──manages──> (1) Directory (root)
Directory (1) ──contains──> (n) FileSystemEntry
FileSystemEntry <|── File
FileSystemEntry <|── Directory
FileSystemEntry (1) ──has──> (1) Metadata
FileSystemEntry (1) ──has──> (1) Permission (v3)
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| FileSystem → Directory (root) | Composition | Root is part of FS |
| Directory → FileSystemEntry | Composition | Entries belong to parent |
| FileSystemEntry → Metadata | Composition | Metadata tied to entry |
| File/Directory → FileSystemEntry | Inheritance | Shared interface |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Composite** | ✅ Yes | Files and directories form tree structure |
| **Singleton** | ✅ Yes | Single file system instance |
| **Visitor** | 🔄 v2 | Operations across tree (search, size calc) |
| **Command** | 🔄 v3 | Undo/redo file operations |
| **Iterator** | ✅ Yes | Directory traversal |

### Pattern Application:

1. **Composite Pattern** - FileSystemEntry
   - File and Directory share common interface
   - Directory contains children (files or directories)
   - Enables recursive operations (delete, size, search)

2. **Singleton Pattern** - FileSystem
   - Single point of access to file system
   - Manages root directory
   - Handles path resolution

3. **Visitor Pattern** (v2) - FileSystemVisitor
   - Search operations across tree
   - Size calculation
   - Permission checking

---

## Step 4: Design Classes

### Core Classes:

#### FileSystem (Singleton)
- **Attributes**: 
  - `root: Directory`
  - `currentDirectory: Directory`
- **Methods**:
  - `createFile(path): File`
  - `createDirectory(path): Directory`
  - `delete(path): boolean`
  - `move(source, destination): boolean`
  - `copy(source, destination): boolean`
  - `find(path, criteria): List<FileSystemEntry>`
  - `resolvePath(path): FileSystemEntry`

#### FileSystemEntry (Abstract - Composite Component)
- **Attributes**:
  - `name: String`
  - `parent: Directory`
  - `metadata: Metadata`
- **Methods**:
  - `getName(): String`
  - `getPath(): String`
  - `getSize(): long`
  - `isFile(): boolean`
  - `isDirectory(): boolean`
  - `delete(): boolean`

#### File (Composite Leaf)
- **Attributes**:
  - `content: String`
- **Methods**:
  - `read(): String`
  - `write(content): void`
  - `append(content): void`
  - `getSize(): long` (returns content length)

#### Directory (Composite Composite)
- **Attributes**:
  - `children: Map<String, FileSystemEntry>`
- **Methods**:
  - `addEntry(entry): boolean`
  - `removeEntry(name): boolean`
  - `getEntry(name): FileSystemEntry`
  - `listEntries(): List<FileSystemEntry>`
  - `getSize(): long` (sum of children sizes)

#### Metadata
- **Attributes**:
  - `createdAt: DateTime`
  - `modifiedAt: DateTime`
  - `accessedAt: DateTime`
  - `owner: String`
- **Methods**:
  - `updateModified(): void`
  - `updateAccessed(): void`

#### Permission (v3)
- **Attributes**:
  - `read: boolean`
  - `write: boolean`
  - `execute: boolean`
- **Methods**:
  - `canRead(): boolean`
  - `canWrite(): boolean`
  - `canExecute(): boolean`

---

## Step 5: Handle Edge Cases

### Input Validation:
- Empty or null path
- Invalid path format (double slashes, invalid chars)
- Path too long (> 100 levels)
- Invalid file/directory names

### Business Logic:
- Create file in non-existent directory
- Delete non-empty directory
- Move/copy to itself
- Circular reference in copy
- Duplicate names in same directory
- Operation on root directory

### Concurrency (v3):
- Simultaneous read/write to same file
- Delete while file is being read
- Move while directory is being traversed
- Concurrent creates in same directory

---

## Step 6: Optimization Opportunities

### Data Structures:
| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Find child by name | O(n) scan | O(1) with HashMap |
| Get full path | O(d) build | Cache path string |
| Search by extension | O(n) full scan | Index by extension |
| Total size | O(n) calculate | Cache + invalidate |

### Caching:
- Cache computed paths
- Cache directory sizes (invalidate on change)
- Index files by extension for fast search

### Indexing:
- `Map<String, FileSystemEntry>` - children by name
- `Map<String, Set<File>>` - files by extension (search index)
- `Set<File>` - all files (for global search)

---

## Step 7: Version Progression

### v1-basic
- File and Directory classes with Composite pattern
- Create, read, write, delete operations
- Basic path resolution
- Simple tree traversal
- Single-threaded

### v2-extended
- Copy and move operations
- Search by name, extension, size
- Metadata (timestamps)
- Recursive size calculation
- Better error handling

### v3-optimized
- Permission system (read/write/execute)
- Symbolic links
- Thread-safe with locks
- Concurrent operations
- File operation undo/redo (Command pattern)

---

## Code Organization

```
file-system/
├── java/
│   ├── v1-basic/
│   │   ├── FileSystem.java        # Singleton + path resolution
│   │   ├── FileSystemEntry.java   # Abstract base (Composite)
│   │   ├── File.java              # Leaf - stores content
│   │   ├── Directory.java         # Composite - contains children
│   │   └── FileSystemDemo.java    # Usage example
│   ├── v2-extended/
│   │   ├── [All v1 classes enhanced]
│   │   ├── Metadata.java          # Timestamps, owner
│   │   └── SearchCriteria.java    # Search parameters
│   └── v3-optimized/
│       ├── [All v2 classes enhanced]
│       ├── Permission.java        # Access control
│       └── SymbolicLink.java      # Link to another entry
└── python/
    └── [Same structure]
```

---

## Interview Discussion Points

1. **Why Composite Pattern for File System?**
   - Files and directories share common operations
   - Enables recursive operations naturally
   - Tree structure maps to file system hierarchy
   - Easy to add new entry types (links, devices)

2. **Path Resolution Strategy?**
   - Parse path into components
   - Start from root or current directory
   - Handle ".." for parent navigation
   - O(d) where d is path depth

3. **How to handle large directories?**
   - HashMap for O(1) child lookup
   - Lazy loading of children
   - Pagination for listing
   - Separate indices for search
