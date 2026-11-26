# Binary Tree Inorder Traversal

- Canonical ID: `lc-0094-binary-tree-inorder-traversal`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Return the inorder traversal of a binary tree: left subtree, node value, then right subtree.

## Driver Signature

- Java: `List<Integer> inorderTraversal(TreeNode root)`
- Python: `inorderTraversal(root: Optional[TreeNode]) -> List[int]`

## Key Cases and Invariants

- An empty tree returns an empty list.
- The iterative version simulates recursion with an explicit stack.

## Solution Ladder

### Tier 1: Recursive DFS

Use recursive calls around the node visit.

- Time: `O(n)` - Every node is visited once.
- Space: `O(h)` - The call stack holds one path of height `h`.

### Tier 2: Iterative stack

Push left descendants, visit, then move right.

- Time: `O(n)` - Each node is pushed and popped once.
- Space: `O(h)` - The stack stores at most one root-to-leaf path.
