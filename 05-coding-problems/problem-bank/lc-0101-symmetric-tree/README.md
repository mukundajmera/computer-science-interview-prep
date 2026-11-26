# Symmetric Tree

## Clean-Room Summary

Given a binary tree, determine whether the left and right sides mirror each other.

## Driver Signature

```java
class Solution {
    public boolean isSymmetric(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8, 4, 4, 2, 6, 6, 2]` | `true` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive mirror check | `O(n)`. | `O(h)`. |
| 2 | Iterative mirror queue | `O(n)`. | `O(w)`. |

## Pitfalls

- Mirror checks compare outside-to-outside and inside-to-inside children.
- A missing node on only one side breaks symmetry.
- Do not compare level values without preserving null structure.
