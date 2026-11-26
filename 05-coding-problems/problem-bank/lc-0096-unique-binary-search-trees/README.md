# Unique Binary Search Trees

- Canonical ID: `lc-0096-unique-binary-search-trees`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Count how many structurally unique binary search trees can be formed with values 1 through n.

## Driver Signature

- Java: `int numTrees(int n)`
- Python: `numTrees(n: int) -> int`

## Key Cases and Invariants

- Choosing a root splits the count into left and right subtree sizes.
- The result is the nth Catalan number.

## Solution Ladder

### Tier 1: Memoized Catalan recursion

Memoize counts by number of nodes and sum each possible root split.

- Time: `O(n^2)` - Each size computes n split products across all sizes.
- Space: `O(n)` - The memo table stores one count per size.

### Tier 2: Bottom-up Catalan DP

Build counts for sizes from zero to n.

- Time: `O(n^2)` - Every size tries every left-subtree size.
- Space: `O(n)` - The DP array stores n plus one counts.
