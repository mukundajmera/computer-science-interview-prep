# Design In-Memory File System

- Canonical ID: `lc-0588-design-in-memory-file-system`
- Difficulty: `hard`
- Status: `verified`

## Clean-Room Problem Summary

Design an in-memory file system supporting directory listing, directory creation, appending content to files, and reading file content.

## Driver Signature

- Java class: `FileSystem`
- Python class: `FileSystem`
- Methods: `['ls', 'mkdir', 'addContentToFile', 'readContentFromFile']`

## Key Cases and Invariants

- Path components form a trie.
- Listing a file returns just that file name.
- Directory listings are sorted lexicographically.

## Solution Ladder

### Tier 1: Path map

Store directory children and file content in maps keyed by full path.

- Time: `O(p log d)` - Operations split path components and listing sorts d names.
- Space: `O(n)` - Maps store all created paths and file content.

### Tier 2: Trie nodes

Represent each path component as a trie node with sorted child names and optional file content.

- Time: `O(p + d log d)` - Traversal follows p components; directory listing sorts d child names.
- Space: `O(n)` - The trie stores every component and file content once.
