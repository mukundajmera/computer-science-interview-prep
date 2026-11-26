# Odd Even Linked List

## Clean-Room Summary

Group nodes by one-based position parity while preserving the original relative order inside each group.

## Driver Signature

```java
class Solution {
    public ListNode oddEvenList(ListNode head) {
        // implement
    }
}
```

```python
class Solution:
    def oddEvenList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # implement
```

## Repo-Authored Cases

- `five nodes alternate`
- `seven nodes`
- `empty list`
- `single node`
- `two nodes unchanged`
- `three nodes move middle after tail`
- `six nodes preserve group order`
## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Buffer nodes | `O(n)`. The list is scanned once to collect nodes and once to relink them. | `O(n)`. The reordered node references are stored in an auxiliary list. |
| 2 | Relink in place | `O(n)`. Each node is visited a constant number of times. | `O(1)`. Only a few pointer variables are needed. |

## Pitfalls

- Odd and even refer to node positions, not node values.
- The even chain tail must be terminated or old next pointers can form a cycle.
