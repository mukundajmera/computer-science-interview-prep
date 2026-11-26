# Same Tree

## Clean-Room Summary

Given two binary trees, decide whether their structures and node values match exactly.

## Driver Signature

```java
class Solution {
    public boolean isSameTree(TreeNode p, TreeNode q) {
        // implementation
    }
}
```

```python
class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `p = [4, 2, 7]`, `q = [4, 2, 7]` | `true` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive pair compare | `O(min(n, m))`. | `O(h)`. |
| 2 | Iterative pair stack | `O(min(n, m))`. | `O(h)`. |

## Pitfalls

- Both null children match; one null child does not.
- Compare structure and value before recursing into children.
- Iterative pair traversal must preserve node pairing.
