# Median of Two Sorted Arrays

## Clean-Room Summary

Given two sorted integer arrays, return the median value of the combined sorted multiset without modifying either input array.

## Driver Signature

```java
class Solution {
    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        // implementation
    }
}
```

```python
class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums1 = [1,4,9], nums2 = [2,6]` | `4.0` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Partial merge until the median position | `O(m + n)`. In the worst case the scan can consume the combined arrays. | `O(1)`. Only the previous and current merged values are retained. |
| 2 | Binary-search partition on the smaller array | `O(log min(m, n))`. The search adjusts one partition boundary each step. | `O(1)`. Partition sentinels and indices are constant-size state. |

## Pitfalls

- For an even combined length, average the two middle values as floating-point numbers.
- Always binary search the smaller array to keep the partition range valid.
- Empty-array boundaries are easiest to handle with sentinel values.
