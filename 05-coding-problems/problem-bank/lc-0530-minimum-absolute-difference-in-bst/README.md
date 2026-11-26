# Minimum Absolute Difference in BST

## Clean-Room Summary

Given a binary search tree, return the smallest absolute difference between values of any two nodes.

## Driver Signature

```java
class Solution {
    public int getMinimumDifference(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def getMinimumDifference(self, root: Optional[TreeNode]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8, 4, 12, 2, 6, 10, 14]` | `2` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive inorder gap scan | `O(n)`. Every node is visited once. | `O(h)`. The recursion stack grows with tree height h. |
| 2 | Iterative inorder stack | `O(n)`. Each node is pushed and popped once. | `O(h)`. The stack stores a root-to-leaf path in a balanced tree and can grow to O(n) when skewed. |

## Pitfalls

- Only neighboring values in inorder order can produce the minimum gap.
- Do not compare a node only with its direct parent; the closest value may be elsewhere in the BST order.
- Initialize the previous value separately from zero so negative or small values are handled correctly.
