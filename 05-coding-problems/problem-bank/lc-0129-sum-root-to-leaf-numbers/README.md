# Sum Root to Leaf Numbers

## Clean-Room Summary

Given a binary tree whose node values are digits, treat each root-to-leaf path as a decimal number and return the sum of all path values.

## Driver Signature

```java
class Solution {
    public int sumNumbers(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[4, 1, 9, 0, 2]` | `871` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive DFS accumulator | `O(n)`. Every tree node is visited once and does O(1) arithmetic. | `O(h)`. The recursion stack is bounded by tree height h, which is O(n) for a skewed tree. |
| 2 | Iterative DFS stack | `O(n)`. Each node is pushed and popped at most once. | `O(h)`. The explicit stack holds one frontier path per active branch, O(h) for balanced traversal and O(n) in the worst skew. |

## Pitfalls

- A leaf is a node with no children, even when it appears before deeper nodes elsewhere.
- Carry the path value down the recursion or stack instead of rebuilding digits at every leaf.
- A null tree contributes zero to the total.
