# Balanced Binary Tree

## Clean-Room Summary

Determine whether every node has left and right subtree heights that differ by at most one.

## Driver Signature

```java
class Solution {
    public boolean isBalanced(TreeNode root) {
        // implement
    }
}
```

```python
class Solution:
    def isBalanced(self, root: Optional[TreeNode]) -> bool:
        # implement
```

## Repo-Authored Cases

- `balanced two-level branch`
- `left chain is too deep`
- `empty tree is balanced`
- `imbalance appears below root`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recompute heights | `O(n^2)`. On a skewed tree, each ancestor recomputes most descendant heights. | `O(n)`. Explicit traversal and height stacks can store many nodes. |
| 2 | Bottom-up height sentinel | `O(n)`. Every node computes its height once. | `O(n)`. The explicit stack and height table can store the tree nodes. |

## Pitfalls

- Height balance must hold at every node, not only at the root.
- Use a sentinel to stop work after finding an imbalance.
- An empty tree is balanced.
- Explicit postorder traversal avoids Python recursion-limit failures on deep trees.
