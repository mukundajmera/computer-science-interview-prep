# Binary Tree Level Order Traversal

## Clean-Room Summary

Given a binary tree, return node values grouped from top level to bottom level.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> levelOrder(TreeNode root) {
        // implementation
    }
}
```

```python
class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[8, 4, 12, 2, 6, 10, 14]` | `[[8], [4, 12], [2, 6, 10, 14]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | BFS level size | `O(n)`. | `O(n)`. |
| 2 | DFS depth buckets | `O(n)`. | `O(n)`. |

## Pitfalls

- Capture the current queue size before processing a level.
- Do not mix nodes from the next level into the current group.
- Empty input returns an empty list.
