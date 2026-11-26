# Longest Increasing Subsequence

## Clean-Room Summary

Given an integer array, return the length of the longest subsequence whose values strictly increase.

## Driver Signature

```java
class Solution {
    public int lengthOfLIS(int[] nums) {
        // implementation
    }
}
```

```python
class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[4, 10, 4, 3, 8, 9]` | `3` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Quadratic DP by ending index | `O(n^2)`. Each pair of indices may be compared once. | `O(n)`. One DP value is stored per input index. |
| 2 | Patience tails with binary search | `O(n log n)`. Each value performs one binary search over the tails array. | `O(n)`. The tails array can grow to length n for a fully increasing input. |

## Pitfalls

- Subsequence values keep original order but do not need to be contiguous.
- Strictly increasing means equal values cannot extend the subsequence.
- The tails array stores candidate endings, not an actual full subsequence.
