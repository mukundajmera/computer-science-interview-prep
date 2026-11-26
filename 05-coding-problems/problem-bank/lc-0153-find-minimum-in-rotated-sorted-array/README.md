# Find Minimum in Rotated Sorted Array

## Clean-Room Summary

Given a rotated sorted array with distinct values, return its minimum value.

## Driver Signature

```java
class Solution {
    public int findMin(int[] nums) {
        // implementation
    }
}
```

```python
class Solution:
    def findMin(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[18, 22, 3, 7, 11, 15]` | `3` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Linear minimum scan | `O(n)`. All n values may need to be checked. | `O(1)`. Only the current best value is stored. |
| 2 | Binary search pivot | `O(log n)`. Each step halves the candidate range. | `O(1)`. Only two boundaries and a midpoint are maintained. |

## Pitfalls

- Compare the midpoint with the right boundary to decide whether the minimum is to the left or right.
- When the subarray is already sorted, the left boundary holds the minimum.
- The distinct-value assumption allows strict movement without duplicate handling.
