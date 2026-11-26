# Reorder List

## Clean-Room Summary

Rewire a linked list in place by alternating nodes from the front and back while preserving node identity.

## Driver Signature

```java
class Solution {
    public void reorderList(ListNode head) {
        // implement
    }
}
```

```python
class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        # implement
```

## Repo-Authored Cases

- `even length`
- `odd length`
- `single node`
- `two nodes unchanged`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Buffer nodes | `O(n)`. Each node is read and linked once. | `O(n)`. The node list stores every node reference. |
| 2 | Split reverse merge | `O(n)`. The list is scanned a constant number of times. | `O(1)`. Only pointer variables are used. |

## Pitfalls

- The LeetCode-compatible signature mutates the list and returns nothing.
- The tail must be terminated to avoid cycles after rewiring.
