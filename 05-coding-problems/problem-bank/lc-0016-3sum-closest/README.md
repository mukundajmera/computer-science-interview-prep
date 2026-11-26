# 3Sum Closest

## Clean-Room Summary

Choose three numbers whose sum is closest to the target and return that sum.

## Driver Signature

```java
class Solution {
    public int threeSumClosest(int[] nums, int target) {
        // implement
    }
}
```

```python
class Solution:
    def threeSumClosest(self, nums: List[int], target: int) -> int:
        # implement
```

## Repo-Authored Cases

- `exact after sorting`
- `exact with mixed signs`
- `target far below all sums`
- `negative and positive exact`
- `closest not exact`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | All triples | `O(n^3)`. Every combination of three indices can be evaluated. | `O(1)`. Only the best sum and loop counters are stored. |
| 2 | Sort and two pointers | `O(n^2)`. Sorting costs O(n log n), then each fixed index runs a linear two-pointer scan. | `O(log n)`. Sorting may use recursion stack space. |

## Pitfalls

- Move the left pointer when the sum is too small and the right pointer when it is too large.
- Return immediately on an exact target match.
