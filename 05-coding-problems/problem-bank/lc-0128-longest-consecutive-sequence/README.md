# Longest Consecutive Sequence

## Clean-Room Summary

Given an unsorted integer array, return the length of the longest run of values that increase by one at each step.

## Driver Signature

```java
class Solution {
    public int longestConsecutive(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Expected | Notes |
|---|---:|---|
| `[10, 5, 6, 7, 20]` | `3` | Run `5, 6, 7`. |
| `[-2, -1, 0, 4]` | `3` | Negative values are handled normally. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort and count consecutive runs | `O(n log n)`. | `O(n)` for sorted copy. |
| 2 | Expand only sequence starts from a set | `O(n)` average. | `O(n)` for distinct values. |

## Pitfalls

- Duplicates should not reset an otherwise consecutive run.
- Only expand from values with no predecessor; otherwise work can become quadratic.
- Empty input returns `0`.
