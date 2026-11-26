# Code Walkthrough: File System

## Overview

In-memory file system with directory hierarchy.

---

## Core Design

```
FileSystem
    │
    └── Directory (root)
            │
            ├── Directory (docs)
            │       ├── File (readme.txt)
            │       └── File (notes.txt)
            │
            └── Directory (images)
                    └── File (photo.jpg)
```

---

## Key Classes

```java
abstract class FileSystemEntity {
    String name;
    Directory parent;
    long createdAt;
}

class File extends FileSystemEntity {
    byte[] content;
    long size;
}

class Directory extends FileSystemEntity {
    Map<String, FileSystemEntity> children;
    
    void addChild(FileSystemEntity entity);
    FileSystemEntity getChild(String name);
    void removeChild(String name);
}
```

---

## Operations

| Operation | Flow |
|-----------|------|
| create file | Navigate to dir → Create file → Add to children |
| read file | Resolve path → Return content |
| delete | Remove from parent's children |
| move | Remove from old → Add to new |
| ls | Return directory's children names |

---

## Interview Questions

### 1. "How to resolve paths?"

```java
FileSystemEntity resolvePath(String path) {
    String[] parts = path.split("/");
    Directory current = root;
    for (String part : parts) {
        if (part.isEmpty()) continue;
        current = (Directory) current.getChild(part);
    }
    return current;
}
```

### 2. "How to handle symbolic links?"

```java
class SymLink extends FileSystemEntity {
    String targetPath;
    
    FileSystemEntity resolve() {
        return fileSystem.resolvePath(targetPath);
    }
}
```

### 3. "How to implement search?"

```java
List<FileSystemEntity> search(Directory dir, String pattern) {
    List<FileSystemEntity> results = new ArrayList<>();
    for (FileSystemEntity entity : dir.children.values()) {
        if (entity.name.matches(pattern)) {
            results.add(entity);
        }
        if (entity instanceof Directory) {
            results.addAll(search((Directory) entity, pattern));
        }
    }
    return results;
}
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Composite** | File/Directory hierarchy |
| **Iterator** | Directory traversal |
| **Visitor** | Operations on tree |
