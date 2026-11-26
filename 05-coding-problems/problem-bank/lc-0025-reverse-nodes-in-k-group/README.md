# Reverse Nodes in k-Group

## Clean-Room Summary

Reverse each complete block of k linked-list nodes while leaving any final incomplete block in its original order.

## Driver Signature

```java
class Solution {
    public ListNode reverseKGroup(ListNode head, int k) {
        // implementation
    }
}
```

```python
class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `head = [1, 2, 3, 4, 5, 6], k = 3` | `[3, 2, 1, 6, 5, 4]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Stack per group | `O(n)`. Each node is pushed and popped at most once. | `O(k)`. The stack stores one complete group of k nodes. |
| 2 | In-place group reversal | `O(n)`. Each node participates in a constant number of pointer operations. | `O(1)`. Only a few node references are maintained. |

## Pitfalls

- Do not reverse a final block whose size is less than k.
- Relink existing nodes rather than rebuilding values.
- Keep the node following the group before rewiring the group.
