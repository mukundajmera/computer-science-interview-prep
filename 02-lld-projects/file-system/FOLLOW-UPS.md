# File System — Follow-Up Questions

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md)

## 1. How would you add permissions?
Introduce ACL metadata per entry and enforce access checks in API methods.

## 2. How would you make search fast at scale?
Maintain secondary indexes by extension/name and update indexes on writes/moves/deletes.

## 3. How would you support snapshots/undo?
Add copy-on-write snapshots or append-only mutation logs with replay.

## 4. How would you make this thread-safe?
Use lock hierarchy (tree-level vs subtree-level) and avoid deadlocks in move/copy.

## 5. How would you support symbolic links?
Add link entry type, cycle detection in traversal, and explicit dereference controls.
