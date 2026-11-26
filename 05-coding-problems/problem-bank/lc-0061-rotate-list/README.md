# Rotate List

## Clean-Room Summary

Given a singly linked list and a non-negative rotation count, move the last `k` nodes to the front after reducing `k` by the list length.

## Driver Signature

```java
class Solution {
    public ListNode rotateRight(ListNode head, int k) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| head | k | Returned list |
|---|---:|---|
| `[8, 3, 5, 1, 9]` | `2` | `[1, 9, 8, 3, 5]` |
| `[4, 6, 7]` | `7` | `[7, 4, 6]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Length count and split | `O(n)`. | `O(1)`. |
| 2 | Circular list then break | `O(n)`. | `O(1)`. |

## Pitfalls

- Use `k % length` so large rotations do not over-walk the list.
- The returned list must reuse the original nodes, not rebuilt nodes with matching values.
- A zero effective rotation should return the original head.
- Always break the temporary circle before returning.
