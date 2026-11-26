# Binary Tree Maximum Path Sum

## Clean-Room Summary

Return the maximum sum obtainable from any nonempty path that follows parent-child links and may start and end at any nodes.

## Driver Signature

```java
class Solution {
    public int maxPathSum(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `root = [4, -2, 6, -1, 3, 5, 7]` | `18` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS gain | `O(n)`. Each tree node is visited once. | `O(h)`. The recursion stack height is h, which can be n for a skewed tree. |

## Pitfalls

- A path can pass through a node using both children, but only one child gain can be returned upward.
- Discard negative child gains when extending a parent path.
- Initialize the best answer from an actual node value, not zero.
