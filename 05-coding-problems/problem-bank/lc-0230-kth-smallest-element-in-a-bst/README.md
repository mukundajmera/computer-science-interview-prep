# Kth Smallest Element in a BST

## Clean-Room Summary

Given a binary search tree and a 1-based rank k, return the kth value in sorted order.

## Driver Signature

```java
class Solution {
    public int kthSmallest(TreeNode root, int k) {
        // implementation
    }
}
```

```python
class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `root = [8, 4, 12, 2, 6, 10, 14]`, `k = 3` | `6` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Iterative inorder early stop | `O(h + k)`. The traversal descends at most h nodes before visiting the first value, then stops after k pops. | `O(h)`. The explicit stack stores the current search path. |
| 2 | Recursive inorder counter | `O(h + k)`. Only nodes needed to reach the kth value are visited, plus the initial descent. | `O(h)`. The recursion stack follows tree height h. |

## Pitfalls

- Inorder traversal gives ascending values only because the input is a BST.
- Stop after k values instead of collecting the whole traversal when possible.
- Treat k as 1-based, not zero-based.
