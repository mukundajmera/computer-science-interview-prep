# Combination Sum IV

## Clean-Room Summary

Count ordered sequences of given positive numbers that add up exactly to the target.

## Driver Signature

```java
class Solution {
    public int combinationSum4(int[] nums, int target) {
        // implement
    }
}
```

```python
class Solution:
    def combinationSum4(self, nums: List[int], target: int) -> int:
        # implement
```

## Repo-Authored Cases

- `ordered small target`
- `no possible sequence`
- `mixed values`
- `single number repeats`
- `order matters with gaps`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Memoized search | `O(target * n)`. Each remainder evaluates all n numbers once. | `O(target)`. Memoization and recursion stack store target-sized state. |
| 2 | Bottom-up DP | `O(target * n)`. Each total considers every number. | `O(target)`. The DP array stores one count per total. |

## Pitfalls

- This counts ordered sequences, so [1,3] and [3,1] are different.
- Loop totals outside and numbers inside for the ordered-sequence recurrence.
