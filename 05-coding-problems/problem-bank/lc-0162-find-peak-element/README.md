# Find Peak Element

## Clean-Room Summary

Return an index whose value is greater than its existing neighbors in a one-dimensional array.

## Driver Signature

```java
class Solution {
    public int findPeakElement(int[] nums) {
        // implementation
    }
}
```

```python
class Solution:
    def findPeakElement(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums = [1, 3, 5, 4, 2]` | `2` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Linear neighbor scan | `O(n)`. Every position may be checked once. | `O(1)`. Only loop variables are stored. |
| 2 | Binary slope | `O(log n)`. Each comparison halves the remaining search interval. | `O(1)`. The search uses two pointers. |

## Pitfalls

- Only existing neighbors need to be compared at array boundaries.
- Binary search follows an increasing slope toward a guaranteed peak.
- Use cases with a unique peak when exact index validation is required.
