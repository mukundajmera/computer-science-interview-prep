# Merge k Sorted Lists

## Clean-Room Summary

Combine several already sorted linked-list chains into one sorted linked-list result.

## Driver Signature

```java
class Solution {
    public ListNode mergeKLists(ListNode[] lists) {
        return null;
    }
}
```

```python
class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        return None
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `lists = [[-4,1,9], null, [-3,2], [0,6,7]]` | `[-4,-3,0,1,2,6,7,9]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Collect, sort, and rebuild | `O(n log n)`. Sorting all values dominates. | `O(n)`. Store all values and build a result chain. |
| 2 | Min heap of current list heads | `O(n log k)`. Each node is processed through a heap of up to `k` heads. | `O(k)`. Store one active node per list in the heap. |

## Pitfalls

- Empty input slots are valid and should be skipped.
- Duplicate values across lists must all appear in the merged output.
- The repo driver checks output values; it does not require reusing the original node identities for this problem.
