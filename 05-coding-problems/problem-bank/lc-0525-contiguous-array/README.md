# Contiguous Array

## Clean-Room Summary

Return the maximum length of a contiguous segment containing the same number of zeroes and ones.

## Driver Signature

```java
class Solution {
    public int findMaxLength(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def findMaxLength(self, nums: List[int]) -> int:
        # implement
```

## Repo-Authored Cases

- `two values balanced`
- `best length two inside three`
- `long middle segment`
- `no balanced segment`
- `whole array balanced`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Prefix brute force | `O(n^2)`. Every pair of interval boundaries can be examined. | `O(n)`. The prefix balance array stores n+1 values. |
| 2 | First balance index | `O(n)`. Each number is processed once and each balance lookup is constant average time. | `O(n)`. The map can store one first index for each distinct balance. |

## Pitfalls

- The balance starts at zero before the array, at index -1.
- Keep the first occurrence of each balance to maximize interval length.
