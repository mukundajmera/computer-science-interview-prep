# Subtree of Another Tree

## Clean-Room Summary

Return whether one binary tree appears as an identical subtree within another binary tree.

## Driver Signature

```java
class Solution {
    public boolean isSubtree(TreeNode root, TreeNode subRoot) {
        // implement
    }
}
```

```python
class Solution:
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        # implement
```

## Repo-Authored Cases

- `subtree matches left branch`
- `extra descendant breaks match`
- `single node match`
- `same values different shape`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Serialize with null markers | `O(n+m)`. Each tree is serialized once and substring search is linear for these built strings. | `O(n+m)`. Both serializations are stored. |
| 2 | DFS tree match | `O(nm)`. In the worst case many candidate roots compare much of the subtree. | `O(h)`. Recursive traversal depth follows tree height. |

## Pitfalls

- Null markers are required when serializing; values alone lose tree shape.
- A matching root value is not enough; structure must match exactly.
