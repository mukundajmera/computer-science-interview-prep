# 🏆 Coach Answer: File System — LLD

> **Type:** Low-Level Design  
> **Difficulty:** Intermediate  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements Clarification (5 min)

### Functional Requirements
1. **Core Operations:** Create, read, write, delete, and list entries.
2. **Navigation:** Resolve absolute (`/root/dir`) and relative paths.
3. **Advanced Operations:** Move, copy, and search.

### Explicit Clarifications
- Q: What entities are needed? → A `FileSystem` (singleton), `Directory` (composite), and `File` (leaf).
- Q: Do we need thread-safety? → Yes, for concurrent operations, especially in `v3-optimized`.
- Q: How are exceptions handled? → Empty/invalid inputs, duplicate operations, and missing parents must be handled explicitly per contract (e.g., returning `null` or `false`, or handling rollback upon failure).
- Q: Are symbolic links in scope? → Yes, in later iterations (v3).

---

## Phase 2 — Core Entities & APIs (10 min)

### Entities
| Entity | Key Responsibilities |
|--------|----------------------|
| `FileSystem` | Singleton entry point, manages the `root` directory, path resolution. |
| `FileSystemEntry` | Abstract base class (Component) for shared attributes (name, parent, metadata). |
| `Directory` | Composite class. Contains a `Map<String, FileSystemEntry>` of children. |
| `File` | Leaf class. Stores `content` (string/bytes) and calculates its size. |

### APIs
- `FileSystem.createFile(path: String, content: String) -> File`
- `FileSystem.createDirectory(path: String) -> Directory`
- `FileSystem.delete(path: String) -> boolean`
- `FileSystem.resolvePath(path: String) -> FileSystemEntry`
- `FileSystem.copy(sourcePath: String, destinationPath: String) -> boolean`
- `FileSystem.move(sourcePath: String, destinationPath: String) -> boolean`
- `File.read() -> String`
- `File.write(content: String) -> void`
- `File.append(content: String) -> void`

---

## Phase 3 — Design Alternatives & Patterns (10 min)

| Pattern | Justification |
|---------|--------------|
| **Composite** | Treats `File` (Leaf) and `Directory` (Composite) uniformly under `FileSystemEntry`. Naturally handles recursive operations (size calculation, deletion, search). |
| **Singleton** | Ensures a single `FileSystem` instance and root directory coordinate the entire structure. |
| **Iterator/Visitor**| Essential for traversing directories, executing search patterns, or calculating cumulative metadata without duplicating logic. |

---

## Phase 4 — Correctness, Complexity & Feature Deltas (10 min)

### Explicit Reference Contracts

1. **Normal use-case**: 
   Creating a file, writing content, and reading it back.
   *Java*:
   ```java
   FileSystem fs = FileSystem.getInstance();
   File file = fs.createFile("/dir/f1.txt", "content");
   fs.writeFile("/dir/f1.txt", "new content");
   String text = fs.readFile("/dir/f1.txt");
   ```
   *Python*:
   ```python
   fs = FileSystem()
   file = fs.create_file("/dir/f1.txt", "content")
   fs.write_file("/dir/f1.txt", "new content")
   text = fs.read_file("/dir/f1.txt")
   ```

2. **Empty/Invalid input**:
   Rejecting `/` creation or `null` paths explicitly.
   *Java*:
   ```java
   public Directory createDirectory(String path) {
       if (path == null || path.isEmpty() || path.equals("/")) {
           throw new IllegalArgumentException("Invalid path");
       }
       // ...
   }
   ```
   *Python*:
   ```python
   def create_directory(self, path: str) -> Optional[Directory]:
       if not path or path == "/":
           raise ValueError("Invalid path")
       # ...
   ```

3. **Duplicate operation**:
   Catching duplicate names in the same directory without overwriting.
   *Java*:
   ```java
   if (parent.hasEntry(dirName)) {
       FileSystemEntry existing = parent.getEntry(dirName);
       if (existing.isDirectory()) {
           return (Directory) existing;
       }
       System.out.println("File exists with same name: " + dirName);
       return null;
   }
   ```
   *Python*:
   ```python
   if parent.has_entry(dir_name):
       existing = parent.get_entry(dir_name)
       if existing.is_directory():
           return existing
       print(f"File exists with same name: {dir_name}")
       return None
   ```

4. **Capacity boundary**:
   Enforcing path limits (100 levels) and string content limits (1GB).
   *Java*:
   ```java
   // In getPathComponents:
   if (comps.length > FileSystem.MAX_PATH_DEPTH) {
       throw new IllegalArgumentException("Path depth exceeds maximum limit");
   }
   // In File.write:
   if (content != null && content.length() > FileSystem.MAX_FILE_SIZE) {
       throw new IllegalArgumentException("File size exceeds maximum limit of 1GB");
   }
   ```
   *Python*:
   ```python
   # In _get_path_components:
   comps = path.split("/")
   if len(comps) > FileSystem.MAX_PATH_DEPTH:
       raise ValueError("Path depth exceeds maximum limit")
   # In File.write:
   if content and len(content) > self.MAX_FILE_SIZE:
       raise ValueError("File size exceeds maximum limit of 1GB")
   ```

5. **Failure rollback**:
   If `move` fails midway (e.g., `copy` fails due to capacity boundary or target exists), the operation reverts and returns `false` safely without deleting the source.
   *Java*:
   ```java
   public boolean move(String sourcePath, String destinationPath) {
       if (!copy(sourcePath, destinationPath)) {
           return false; // Rollback, source remains intact
       }
       return delete(sourcePath);
   }
   ```
   *Python*:
   ```python
   def move(self, source_path: str, destination_path: str) -> bool:
       if not self.copy(source_path, destination_path):
           return False # Rollback, source remains intact
       return self.delete(source_path)
   ```

### Complexity
- **Time**: 
  - Lookup/Resolve: O(d) where `d` is the path depth (using `HashMap` for O(1) child lookups).
  - Search: O(N) where `N` is the number of nodes in the subtree.
- **Space**: O(F + D) where `F` is total files and `D` is total directories in memory. 

### Version-Specific Deltas
- **v1-basic**: Single-threaded, pure in-memory composite structure. Focuses on tree traversal and standard path manipulations.
- **v2-extended**: Adds metadata, timestamps, and robust search strategies.
- **v3-optimized**: Introduces permissions (read/write/execute), symbolic links, and lock-based thread safety for `FileSystemEntry` nodes. 

Public APIs and version-specific feature deltas are documented. Focused tests target specific versions rather than silently importing `v1`.

---

## Phase 5 — Failure & Concurrency Discussion (10 min)

### Concrete Failure Trace
**Scenario:** A thread attempts to `move` `/docs/notes.txt` to `/archive/notes.txt` while another thread attempts to `delete` `/docs/notes.txt`.
- **Failure:** Without locks, `move` might extract the entry from `/docs` just as `delete` drops it. The reference may be lost or duplicate orphaned entries created, leading to a race condition that corrupts the in-memory tree.
- **Solution:** In `v3-optimized`, apply a granular locking mechanism (e.g., locking both the source parent and destination parent directories sequentially, avoiding deadlocks by locking in lexicographical path order). If the lock acquisition fails, or the file vanishes before acquisition (e.g., `delete` executed first), the operation catches the failure, throws a `ConcurrentModificationException`, and executes a clean rollback, ensuring the file system remains atomic and consistent.

---

## Phase 6 — Wrap-Up

### Limitations
- String-based content limits realistic memory handling.
- Large directories might necessitate a B-Tree or pagination rather than a single `HashMap`.
