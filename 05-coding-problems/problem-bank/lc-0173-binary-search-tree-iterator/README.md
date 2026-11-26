# Binary Search Tree Iterator

## Clean-Room Summary

Expose a sorted iterator over a binary search tree so callers can repeatedly ask whether another value exists and retrieve the next smallest value.

## Driver Signature

```java
class BSTIterator {
    public BSTIterator(TreeNode root) {}
    public int next() { return 0; }
    public boolean hasNext() { return false; }
}
```

```python
class BSTIterator:
    def __init__(self, root: Optional[TreeNode]) -> None:
        pass
    def next(self) -> int:
        return 0
    def hasNext(self) -> bool:
        return False
```

## Repo-Authored Examples

| Operations | Results |
| --- | --- |
| `BSTIterator([8,4,12,2,6,10,14]), hasNext(), next(), next(), hasNext()` | `null, true, 2, 4, true` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Flattened inorder list | `O(n)` construction, `O(1)` per iterator call. The whole traversal is precomputed. | `O(n)`. Store every value. |
| 2 | Controlled inorder stack | `O(1)` amortized `next`, `O(1)` `hasNext`. Each node is pushed and popped once. | `O(h)`. Store only the current frontier path. |

## Pitfalls

- `hasNext()` should not advance the iterator.
- The stack tier must push all left descendants of a right child after returning a node.
- The constructor should prepare the first smallest node, not wait until `next()` has no state.
