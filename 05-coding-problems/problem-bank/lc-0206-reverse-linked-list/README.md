# Reverse Linked List

## Clean-Room Summary

Given the head of a singly linked list, return the head of a chain with the same values in reverse order.

## Driver Signature

```java
class Solution {
    public ListNode reverseList(ListNode head) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| head | Returned list |
|---|---|
| `[4, 1, 9]` | `[9, 1, 4]` |
| `null` | `null` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Copy values into a reversed chain | `O(n)`. | `O(n)`. |
| 2 | In-place pointer reversal | `O(n)`. | `O(1)`. |

## Pitfalls

- Save the next node before rewiring the current node.
- Return the new front of the reversed chain, not the original head.
- Treat an empty chain as a valid input that returns an empty chain.
