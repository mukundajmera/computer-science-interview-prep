# Binary Tree Right Side View

## Clean-Room Summary

Given a binary tree, return the node value visible from the right side at each depth.

## Driver Signature

```java
class Solution {
    public List<Integer> rightSideView(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8, 4, 12, 2, 6, 10, 14]` | `[8, 12, 14]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Level-order last node | `O(n)`. | `O(n)`. |
| 2 | Right-first DFS | `O(n)`. | `O(h)`. |

## Pitfalls

- Keep one value per depth.
- Right-first DFS records the first node seen at a depth.
- BFS should record the last node in each level.
