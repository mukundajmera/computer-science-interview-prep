# Palindrome Linked List

## Clean-Room Summary

Given a singly linked list, decide whether its values read the same from front to back and back to front.

## Driver Signature

```java
class Solution {
    public boolean isPalindrome(ListNode head) {
        // implementation
    }
}
```

```python
from typing import Optional


class Solution:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        # implementation
```

## Repo-Authored Examples

| head | Palindrome? |
|---|---|
| `[2, 4, 4, 2]` | `true` |
| `[9, 1, 9, 2]` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Copy values and compare ends | `O(n)`. | `O(n)`. |
| 2 | Reverse the second half in place and restore it | `O(n)`. | `O(1)`. |

## Pitfalls

- Skip the center node for odd-length lists before comparing halves.
- Compare values, not node identity.
- If the list may need to be preserved by a caller, restore the reversed second half after the check.
