# Invert Binary Tree

## Clean-Room Summary

Given a binary tree, swap every node's left and right child and return the root.

## Driver Signature

```java
class Solution {
    public TreeNode invertTree(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8, 4, 12, 2, 6, 10, 14]` | `[8, 12, 4, 14, 10, 6, 2]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive child swap | `O(n)`. | `O(h)`. |
| 2 | Iterative stack swap | `O(n)`. | `O(h)`. |

## Pitfalls

- Swap before or after recursive child work, but do it consistently.
- Return the original root after in-place rewiring.
- Empty input should return an empty tree.
