# Remove Duplicates from Sorted Array II

## Clean-Room Summary

Given a sorted integer array, compact it in place so each distinct value appears at most twice and return the kept prefix length.

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

| nums | Kept prefix length | Kept prefix |
|---|---:|---|
| `[0, 0, 0, 1, 1, 2, 2, 2, 3]` | `7` | `[0, 0, 1, 1, 2, 2, 3]` |
| `[5, 5, 5, 5]` | `2` | `[5, 5]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Count current run while writing | `O(n)`. | `O(1)`. |
| 2 | Compare against two-back prefix | `O(n)`. | `O(1)`. |

## Pitfalls

- Values after the returned prefix are irrelevant and should not be asserted by tests.
- The sorted order lets the algorithm decide from the already kept prefix whether another duplicate is allowed.
- Arrays shorter than three are already valid.
