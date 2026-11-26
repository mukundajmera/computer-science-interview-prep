# All Nodes Distance K in Binary Tree

- Canonical ID: `lc-0863-all-nodes-distance-k-in-binary-tree`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Return the values of all tree nodes exactly k edges away from a target node in the same binary tree.

## Driver Signature

- Java: `List<Integer> distanceK(TreeNode root, TreeNode target, int k)`
- Python: `distanceK(root: Optional[TreeNode], target: Optional[TreeNode], k: int) -> List[int]`

## Key Cases and Invariants

- Distance can move downward into children or upward through ancestors.
- The returned values are a set, so order is not semantically important.
- A target with k = 0 returns only the target value.

## Solution Ladder

### Tier 1: Parent map BFS

Record parent pointers, then BFS from the target over left, right, and parent edges.

- Time: `O(n)` - Each node is visited a constant number of times.
- Space: `O(n)` - Parent map, queue, and visited set can store every node.

### Tier 2: Distance DFS

Recursively find target distance from each ancestor and collect downward nodes from the opposite branch at the remaining distance.

- Time: `O(n)` - Each node participates in at most a constant amount of traversal.
- Space: `O(h)` - The recursion stack is tree height, excluding the output list.
