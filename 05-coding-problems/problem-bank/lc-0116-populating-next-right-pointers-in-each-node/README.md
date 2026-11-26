# Populating Next Right Pointers In Each Node

- Canonical ID: `lc-0116-populating-next-right-pointers-in-each-node`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Populate each node's `next` pointer to its neighbor on the same level in a perfect binary tree.

## Driver Signature

- Java: `Node connect(Node root)`
- Python: `connect(root: Optional[Node]) -> Optional[Node]`

## Key Cases and Invariants

- The final node on each level points to null.
- The perfect-tree constraint enables a constant-space level-linking solution.

## Solution Ladder

### Tier 1: Level-order queue

Traverse level by level and link adjacent nodes in the queue slice.

- Time: `O(n)` - Each node is enqueued and linked once.
- Space: `O(w)` - The queue can store one level of width w.

### Tier 2: Perfect-tree pointer walk

Use established next pointers on the current level to wire the next level.

- Time: `O(n)` - Every non-leaf wires two child links once.
- Space: `O(1)` - Only current-level pointers are stored.
