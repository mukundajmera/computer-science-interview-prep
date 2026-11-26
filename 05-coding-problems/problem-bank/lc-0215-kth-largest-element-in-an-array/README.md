# Kth Largest Element in an Array

## Clean-Room Summary

Return the value that would appear in position k if the array were sorted from largest to smallest.

## Driver Signature

```java
class Solution {
    public int findKthLargest(int[] nums, int k) {
        // implementation
    }
}
```

```python
class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums = [12, 4, 7, 7, 19], k = 2` | `12` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort descending | `O(n log n)`. Comparison sorting dominates the work. | `O(log n) to O(n)`. Java's in-place primitive sort uses stack space, while Python's list sort may allocate temporary merge buffers. |
| 2 | Min-heap size k | `O(n log k)`. Each value may trigger one heap operation bounded by heap size k. | `O(k)`. The heap stores at most k values. |
| 3 | Quickselect | `O(n) average, O(n^2) worst`. Balanced partitions inspect linear total work on average, but unlucky pivots can repeatedly shrink by one. | `O(1)`. Partitioning is in place. |

## Pitfalls

- k is one-based in descending order; convert it to an ascending target index for quickselect.
- Duplicates count as separate positions.
- A fixed deterministic pivot is simple but has quadratic worst-case behavior.
