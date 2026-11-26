# Sort List

## Clean-Room Summary

Return a linked list containing the same values as the input list in ascending order.

## Driver Signature

```java
class Solution {
    public ListNode sortList(ListNode head) {
        // implementation
    }
}
```

```python
class Solution:
    def sortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `head = [8, 3, 5, 1]` | `[1, 3, 5, 8]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Array sort rebuild | `O(n log n)`. Sorting the copied values dominates the traversal and rebuild work. | `O(n)`. The value array and rebuilt nodes store n items. |
| 2 | Linked-list merge sort | `O(n log n)`. Each level merges all nodes and there are logarithmically many split levels. | `O(log n)`. The recursive call stack stores one frame per split level while nodes are relinked in place. |

## Pitfalls

- Break the list at the midpoint before recursing or the same nodes will be revisited.
- Merge by relinking existing nodes to avoid extra node allocation in the optimized version.
- Return an empty serialized list for a null input head.
