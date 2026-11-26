# File System — Common Pitfalls

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

## 1. Treating paths as raw strings only
Missing normalization for `.` and `..` leads to inconsistent behavior.

## 2. Breaking parent-child invariants
Move/copy/delete implementations that do not update parent pointers drift the tree.

## 3. Allowing illegal root mutations
Deleting root or assigning an invalid root name destabilizes the entire structure.

## 4. Copying directories into their descendants
Without cycle-prevention checks, recursive copy can explode or loop.

## 5. Ignoring explicit failure contracts
Ambiguous behavior for missing paths, type mismatches, and duplicate names hurts API reliability.
