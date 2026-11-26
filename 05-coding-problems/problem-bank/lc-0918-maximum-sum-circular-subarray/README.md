# Maximum Sum Circular Subarray

## Clean-Room Summary

Find the largest sum of a non-empty contiguous segment when the array can wrap from the end back to the start.

## Driver Signature

```java
class Solution {
    public int maxSubarraySumCircular(int[] nums) {
        // implementation
    }
}
```

```python
class Solution:
    def maxSubarraySumCircular(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums = [6, -2, 4, -1]` | `9` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Brute force doubled window | `O(n^2)`. There are n starts and each start extends up to n positions. | `O(1)`. Only counters and the best sum are tracked. |
| 2 | Kadane max/min | `O(n)`. Each value updates constant-time Kadane states once. | `O(1)`. Only running sums and extrema are stored. |

## Pitfalls

- When every value is negative, total minus minimum would select an empty segment; use the normal Kadane answer.
- The wrapped segment is the complement of the minimum-sum middle segment.
- The chosen subarray must be non-empty.
