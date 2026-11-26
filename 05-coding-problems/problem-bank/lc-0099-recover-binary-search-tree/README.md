# Recover Binary Search Tree

- Canonical ID: `lc-0099-recover-binary-search-tree`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Recover a binary search tree where exactly two node values were swapped, without changing the tree shape.

## Driver Signature

- Java: `void recoverTree(TreeNode root)`
- Python: `recoverTree(root: Optional[TreeNode]) -> None`

## Key Cases and Invariants

- An inorder traversal of a valid BST is sorted.
- One or two inversions reveal the misplaced nodes.

## Solution Ladder

### Tier 1: Sort inorder values

Collect nodes and sorted values, then write sorted values back in inorder order.

- Time: `O(n log n)` - Sorting n values dominates traversal.
- Space: `O(n)` - Nodes and values are stored.

### Tier 2: Detect inorder inversions

Track the previous inorder node and swap the two values that violate sorted order.

- Time: `O(n)` - The tree is traversed once.
- Space: `O(h)` - The recursion stack stores a path of height h.
