# Unique Binary Search Trees II

- Canonical ID: `lc-0095-unique-binary-search-trees-ii`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Generate every structurally unique binary search tree that stores values from 1 through n.

## Driver Signature

- Java: `List<TreeNode> generateTrees(int n)`
- Python: `generateTrees(n: int) -> List[Optional[TreeNode]]`

## Key Cases and Invariants

- Choosing each value as root splits the remaining values into independent left and right ranges.
- The driver compares returned trees as an unordered list of level-order tree encodings.

## Solution Ladder

### Tier 1: Recursive range product

Try each value as root and combine every left-range tree with every right-range tree.

- Time: `O(C_n * n)` - The Catalan number `C_n` trees are produced and each tree has up to n nodes.
- Space: `O(C_n * n)` - The output stores all generated trees; recursion depth is linear.
