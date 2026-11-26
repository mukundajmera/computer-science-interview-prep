# Linked List Cycle

## Clean-Room Summary

Given the head of a singly linked list, determine whether following `next` pointers can revisit a node instead of eventually reaching the end.

## Driver Signature

```java
class Solution {
    public boolean hasCycle(ListNode head) {
        return false;
    }
}
```

```python
from typing import Optional


class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        return False
```

## Repo-Authored Examples

The repository driver represents a cyclic fixture as `{"values": [...], "cycleTo": i}`, where the final node points back to the node at index `i`.

| head fixture | Output |
|---|---|
| `{"values": [6,1,8,5], "cycleTo": 2}` | `true` |
| `{"values": [4,7], "cycleTo": 0}` | `true` |
| `[1,2,3,4]` | `false` |
| `[5,5]` | `false` |
| `null` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Track visited node identities | `O(n)`. Each reachable node is inspected once until a repeat or the end. | `O(n)`. The set can store every reachable node. |
| 2 | Floyd fast and slow pointers | `O(n)`. Pointer movement is linear in the number of reachable nodes. | `O(1)`. Only two references are needed. |

## Pitfalls

- Compare node identity, not node values; duplicate values do not imply a cycle.
- In Floyd's algorithm, advance the fast pointer only after checking that both required links exist.
- A one-node list can still contain a cycle if the node points to itself.
