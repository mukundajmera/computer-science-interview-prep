# Subarray Sum Equals K

## Clean-Room Summary

Count contiguous subarrays whose elements sum exactly to k.

## Driver Signature

```java
class Solution {
    public int subarraySum(int[] nums, int k) {
        // implement
    }
}
```

```python
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        # implement
```

## Repo-Authored Cases

- `two short matches`
- `prefix and singleton matches`
- `zero target with negative`
- `all zeroes`
- `negative target mix`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Running-sum brute force | `O(n^2)`. Every start/end pair can be inspected. | `O(1)`. Only counters and the current sum are stored. |
| 2 | Prefix counts | `O(n)`. Each number performs one map lookup and update. | `O(n)`. The prefix-count map can store one entry per index. |

## Pitfalls

- Sliding window is not valid when negative numbers are allowed.
- Seed the prefix map with sum zero once to count subarrays starting at index zero.
