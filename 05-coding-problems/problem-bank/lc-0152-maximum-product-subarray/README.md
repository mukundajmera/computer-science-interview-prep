# Maximum Product Subarray

## Clean-Room Summary

Find the maximum product of a non-empty contiguous subarray, accounting for sign flips from negative values.

## Driver Signature

```java
class Solution {
    public int maxProduct(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        # implement
```

## Repo-Authored Cases

- `negative pair boosts product`
- `zero splits ranges`
- `three negatives`
- `single negative`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | All subarray products | `O(n^2)`. There are O(n^2) contiguous subarrays. | `O(1)`. Only running and best products are stored. |
| 2 | Running max and min products | `O(n)`. Each number updates two scalar states once. | `O(1)`. Only current max, current min, and best product are stored. |

## Pitfalls

- Track the minimum product as well as the maximum.
- A zero resets any product crossing it.
- The answer must be non-empty, so initialize from `nums[0]`.
