# Remove Duplicates from Sorted Array

## Clean-Room Summary

Given a sorted array, compact it so each distinct value appears once in the prefix and return the number of distinct values.

## Driver Signature

```java
class Solution {
    public int removeDuplicates(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| nums | Return | Required prefix |
|---|---:|---|
| `[1, 2, 2, 2, 5, 5, 9]` | `4` | `[1, 2, 5, 9]` |
| `[-3, -3, -1, 0, 0, 4]` | `4` | `[-3, -1, 0, 4]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Copy unique values into an extra list | `O(n)`. | `O(n)`. |
| 2 | In-place write pointer over sorted groups | `O(n)`. | `O(1)`. |

## Pitfalls

- The sorted input lets you detect duplicates by comparing with the last kept value.
- Return the prefix length, not the last written index.
- The driver validates only the prefix described by the returned length.
