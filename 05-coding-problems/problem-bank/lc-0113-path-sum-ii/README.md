# Path Sum II

## Clean-Room Summary

Return all root-to-leaf value paths whose sum equals the target.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> pathSum(TreeNode root, int targetSum) {
        // implement
    }
}
```

```python
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> List[List[int]]:
        # implement
```

## Repo-Authored Cases

- `two matching leaves`
- `no matching leaf`
- `single matching root`
- `negative values`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Copy paths | `O(nh)`. Each node can copy a root-to-node path of length up to h. | `O(nh)`. Copied paths across recursion can accumulate with path length. |
| 2 | Backtracking | `O(nh)`. Traversal visits n nodes and copies each matching path of length up to h. | `O(h)`. The working path and recursion stack follow tree height, excluding output. |

## Pitfalls

- Only root-to-leaf paths count; stopping at an internal node is wrong.
- Copy the path when recording an answer so later backtracking does not mutate it.
