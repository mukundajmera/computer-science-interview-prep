# Remove Nth Node From End of List

## Clean-Room Summary

Given a singly linked list and a one-based position counted from the tail, return the list after removing that node.

## Driver Signature

```java
class Solution {
    public ListNode removeNthFromEnd(ListNode head, int n) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| head | n | Returned list |
|---|---:|---|
| `[8, 4, 6, 2]` | `2` | `[8, 4, 2]` |
| `[5, 7]` | `2` | `[7]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Copy values except the target | `O(n)`. | `O(n)`. |
| 2 | Two-pointer gap deletion | `O(n)`. | `O(1)`. |

## Pitfalls

- A dummy node simplifies removing the head.
- Advance the fast pointer exactly `n` steps before moving both pointers.
- Deleting the only node should return an empty chain.
