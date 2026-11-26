# Insertion Sort List

## Clean-Room Summary

Given the head of a singly linked list, sort the list using insertion sort, and return the sorted list's head.

## Driver Signature

```java
class Solution {
    public ListNode insertionSortList(ListNode head) {
        // implementation
    }
}
```

```python
class Solution:
    def insertionSortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `head = [4,2,1,3]` | `[1,2,3,4]` |
| `head = [-1,5,3,4,0]` | `[-1,0,3,4,5]` |
| `head = []` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Dummy head insertion | `O(n^2)`. Walks sorted chain to place each node. | `O(1)`. Rearranges node references in-place. |

## Pitfalls

- Re-wire pointers carefully so nodes are not detached or cyclically referenced during extraction and insertion.
- When the next node is already greater than or equal to the current tail of the sorted section, simply advance the pointer to achieve $O(n)$ best-case runtime on sorted inputs.
