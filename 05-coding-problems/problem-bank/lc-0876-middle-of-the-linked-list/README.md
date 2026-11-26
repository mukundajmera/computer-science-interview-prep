# Middle of the Linked List

## Clean-Room Summary

Given the head of a singly linked list, return the node that begins the middle suffix. If the list has two middle nodes, return the second one.

## Driver Signature

```java
class Solution {
    public ListNode middleNode(ListNode head) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| head | Returned suffix |
|---|---|
| `[10, 20, 30, 40, 50]` | `[30, 40, 50]` |
| `[4, 8, 15, 16]` | `[15, 16]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Count length then walk to the middle | `O(n)`. | `O(1)`. |
| 2 | Slow and fast pointers | `O(n)`. | `O(1)`. |

## Pitfalls

- For an even-length list, return the second middle node.
- Returning a newly built suffix would match values but not the linked-list node contract.
- Moving `fast` two steps at a time avoids needing a separate length pass.
- Returning the middle node means the output contains every node from that point onward.
