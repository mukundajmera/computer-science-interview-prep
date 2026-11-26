# Partition List

## Clean-Room Summary

Given a singly linked list and a pivot value, return a stable partition where nodes with values below the pivot appear before the remaining nodes.

## Driver Signature

```java
class Solution {
    public ListNode partition(ListNode head, int x) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def partition(self, head: Optional[ListNode], x: int) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| head | x | Returned list |
|---|---:|---|
| `[5, 1, 4, 2, 6, 3]` | `4` | `[1, 2, 3, 5, 4, 6]` |
| `[7, 5, 6]` | `4` | `[7, 5, 6]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Collect original nodes into two partitions | `O(n)`. | `O(n)`. |
| 2 | Two dummy chains | `O(n)`. | `O(1)`. |

## Pitfalls

- Preserve original relative order inside each partition.
- Terminate the right partition tail to avoid retaining stale links.
- Store and relink node references when using arrays; copying values into new nodes changes the linked-list contract.
- Values equal to the pivot belong in the right partition.
