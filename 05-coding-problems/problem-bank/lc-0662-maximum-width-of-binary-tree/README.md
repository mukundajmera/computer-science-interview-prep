# Maximum Width of Binary Tree

## Clean-Room Summary

Measure the widest level using the positions nodes would occupy in a complete binary tree, including gaps between existing nodes.

## Driver Signature

```java
class Solution {
    public int widthOfBinaryTree(TreeNode root) {
        // implement
    }
}
```

```python
class Solution:
    def widthOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        # implement
```

## Repo-Authored Cases

- `missing middle creates width`
- `single node`
- `full first level`
- `left chain`
- `outer grandchildren`
- `deep sparse outer nodes`
## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS indexes | `O(n)`. Every tree node is visited once. | `O(h)`. The recursion stack and per-depth first indexes scale with tree height. |
| 2 | Normalized BFS | `O(n)`. Every node enters and leaves the queue once. | `O(w)`. The queue stores one level at a time, where w is the maximum real node count on a level. |

## Pitfalls

- Width counts missing positions between the leftmost and rightmost nodes on a level.
- Normalize indexes per level to avoid unnecessary growth in deep sparse trees.
