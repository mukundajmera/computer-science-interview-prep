# Validate Binary Search Tree

## Clean-Room Summary

Return whether every node in a binary tree satisfies the strict lower and upper bounds required by a binary search tree.

## Driver Signature

```java
class Solution {
    public boolean isValidBST(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8, 4, 12, 2, 6, 10, 14]` | `true` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive ancestor bounds | `O(n)`. Every node is checked once until a violation is found. | `O(h)`. The recursion stack follows tree height h. |
| 2 | Iterative bound frames | `O(n)`. Each node is popped from the stack once unless validation fails early. | `O(h)`. The stack stores active branches; in the worst skewed case this can be O(n). |

## Pitfalls

- Each node must fit all ancestor bounds, not only compare with its direct parent.
- The BST relation is strict; duplicate values are invalid.
- Use bounds wider than int values in Java to avoid edge overflow.
