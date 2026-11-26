# Partition Equal Subset Sum

## Clean-Room Summary

Decide whether the array can be split into two groups with equal sum.

## Driver Signature

```java
class Solution {
    public boolean canPartition(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def canPartition(self, nums: List[int]) -> bool:
        # implement
```

## Repo-Authored Cases

- `can split into equal halves`
- `odd total cannot split`
- `single pair`
- `needs non-greedy choice`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Memoized target search | `O(nS)`. There are n indices and S possible remaining sums up to the target. | `O(nS)`. The memo table stores reachable index/remaining states. |
| 2 | One-dimensional subset DP | `O(nS)`. Each number scans sums up to the target S. | `O(S)`. The reachable table stores one boolean per target sum. |

## Pitfalls

- Reject odd total sums immediately.
- Update one-dimensional DP backward so each number is used at most once.
- The target is half of the total, not the full sum.
