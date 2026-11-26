# Remove Duplicates from Sorted List II

## Clean-Room Summary

Given a sorted linked list, keep only values that appear exactly once and remove every node from duplicated value runs.

## Driver Signature

```java
class Solution {
    public ListNode deleteDuplicates(ListNode head) {
        // implementation
    }
}
```

```python
class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `head = [1, 1, 2, 3, 3, 4]` | `[2, 4]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Count then relink | `O(n)`. The list is scanned once for counts and once for relinking. | `O(u)`. The count map stores one entry per distinct value. |
| 2 | Sentinel run skip | `O(n)`. Each node is visited as part of exactly one sorted run. | `O(1)`. Only pointer references are used beyond the list itself. |

## Pitfalls

- Remove the entire duplicate run, not just extra copies.
- A sentinel node handles duplicate runs at the head.
- Detach the tail after relinking unique nodes.
