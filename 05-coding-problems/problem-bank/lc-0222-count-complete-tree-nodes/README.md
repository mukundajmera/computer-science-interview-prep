# Count Complete Tree Nodes

## Clean-Room Summary

Given a complete binary tree, count its nodes faster than a plain traversal when possible.

## Driver Signature

```java
class Solution {
    public int countNodes(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def countNodes(self, root: Optional[TreeNode]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8, 4, 12, 2, 6, 10, 14]` | `7` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Full DFS count | `O(n)`. | `O(h)`. |
| 2 | Complete-tree height pruning | `O(log^2 n)`. | `O(log n)`. |

## Pitfalls

- The height optimization relies on the tree being complete.
- A perfect subtree with height h contains 2^h - 1 nodes.
- The empty tree count is zero.
