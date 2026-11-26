# Add Two Numbers

## Clean-Room Summary

Given two non-empty linked lists whose nodes store base-10 digits from least significant to most significant, return a linked list representing their sum in the same digit order.

## Driver Signature

```java
class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| l1 | l2 | Returned list |
|---|---|---|
| `[4, 2, 7]` | `[6, 8]` | `[0, 1, 8]` |
| `[9, 9]` | `[1]` | `[0, 0, 1]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Copy digits before adding | `O(max(m, n))`. | `O(m + n)`. |
| 2 | Stream digits with carry | `O(max(m, n))`. | `O(1)`. |

## Pitfalls

- Carry must be processed even after both input lists are exhausted.
- Missing nodes contribute digit zero while the other list continues.
- The result order remains least-significant digit first.
