# Path Sum

## Clean-Room Summary

Given a binary tree and target sum, decide whether any root-to-leaf path totals the target.

## Driver Signature

```java
class Solution {
    public boolean hasPathSum(TreeNode root, int targetSum) {
        // implementation
    }
}
```

```python
class Solution:
    def hasPathSum(self, root: Optional[TreeNode], targetSum: int) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `root = [8, 4, 12, 2, 6, 10, 14]`, `targetSum = 30` | `true` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive remaining sum | `O(n)`. | `O(h)`. |
| 2 | Iterative node sums | `O(n)`. | `O(h)`. |

## Pitfalls

- Only root-to-leaf paths count.
- Subtract as you descend so the leaf check is local.
- An empty tree has no valid path even for target zero.
