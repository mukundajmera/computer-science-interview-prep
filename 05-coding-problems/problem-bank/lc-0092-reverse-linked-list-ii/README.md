# Reverse Linked List II

## Clean-Room Summary

Given a singly linked list and one-based inclusive positions, reverse only that segment and return the head of the resulting list.

## Driver Signature

```java
class Solution {
    public ListNode reverseBetween(ListNode head, int left, int right) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| head | left | right | Returned list |
|---|---:|---:|---|
| `[7, 2, 5, 8, 1]` | `2` | `4` | `[7, 8, 5, 2, 1]` |
| `[3, 6, 9]` | `1` | `2` | `[6, 3, 9]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Detach segment then reverse | `O(n)`. | `O(1)`. |
| 2 | In-place head insertion | `O(n)`. | `O(1)`. |

## Pitfalls

- Positions are one-based, so walk `left - 1` times from the dummy node.
- A single-position range is already reversed.
- Reverse links between existing nodes; do not rebuild a value-equivalent list.
- Keep the node before the segment fixed while moving nodes to the front of the segment.
