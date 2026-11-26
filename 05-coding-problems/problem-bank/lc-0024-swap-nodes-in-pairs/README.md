# Swap Nodes in Pairs

## Clean-Room Summary

Given a singly linked list, swap every adjacent pair of nodes and return the new head. A leftover final node stays in place.

## Driver Signature

```java
class Solution {
    public ListNode swapPairs(ListNode head) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| head | Returned list |
|---|---|
| `[9, 4, 7, 2]` | `[4, 9, 2, 7]` |
| `[5, 1, 8]` | `[1, 5, 8]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive pair rewiring | `O(n)`. | `O(n)`. |
| 2 | Iterative pair rewiring | `O(n)`. | `O(1)`. |

## Pitfalls

- Save the node after the pair before rewiring links.
- A dummy node avoids special handling for the new head.
- Rebuilding nodes can pass value-only tests but violates the linked-list node contract.
- Do not modify the final unpaired node.
