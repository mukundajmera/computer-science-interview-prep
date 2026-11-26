# Merge Two Sorted Lists

## Clean-Room Summary

Given two sorted singly linked lists, return one sorted chain containing every value from both inputs.

## Driver Signature

```java
class Solution {
    public ListNode mergeTwoLists(ListNode list1, ListNode list2) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| list1 | list2 | Returned list |
|---|---|---|
| `[0, 3, 8]` | `[1, 4, 7]` | `[0, 1, 3, 4, 7, 8]` |
| `[]` | `[-2, 5]` | `[-2, 5]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Collect values, sort, and rebuild | `O((m + n) log(m + n))`. | `O(m + n)`. |
| 2 | Iterative pointer splice | `O(m + n)`. | `O(1)`. |

## Pitfalls

- Preserve sorted order when duplicate or negative values appear.
- Return the non-empty chain directly when one input is empty.
- In the optimized approach, move the tail pointer immediately after attaching a node.
