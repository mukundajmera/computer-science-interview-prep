# Copy List with Random Pointer

## Clean-Room Summary

Deep-copy a linked list where each node has both `next` and `random` pointers. The clone must preserve values, next order, and random relationships without reusing any original node object.

## Driver Signature

```java
class Solution {
    public Node copyRandomList(Node head) {
        // return copied head
    }
}
```

```python
from typing import Optional


class Solution:
    def copyRandomList(self, head: Optional[Node]) -> Optional[Node]:
        # return copied head
```

## Repo-Authored Examples

Fixtures are normalized as `[value, randomIndex]` rows. `randomIndex` is `null` when the random pointer is absent.

| Input head | Expected copy |
|---|---|
| `[[8,null],[12,0],[5,2],[19,1]]` | `[[8,null],[12,0],[5,2],[19,1]]` |
| `[[4,1],[9,0]]` | `[[4,1],[9,0]]` |
| `[]` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Hash map old nodes to clones | `O(n)`. Allocate and wire each node once. | `O(n)`. Store old-to-new mappings. |
| 2 | Weave clones into the original list | `O(n)`. Three linear passes over the list. | `O(1)`. No auxiliary map beyond output nodes. |

## Pitfalls

- Returning the original head is invalid even if the normalized values match.
- Random pointers may point backward, forward, to self, or to nothing.
- The copied list should be detached from the original list after the weaving approach.
