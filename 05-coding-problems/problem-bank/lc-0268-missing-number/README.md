# Missing Number

## Clean-Room Summary

Given distinct values drawn from 0 through n with one value absent, return the absent value.

## Driver Signature

```java
class Solution {
    public int missingNumber(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def missingNumber(self, nums: List[int]) -> int:
        # implement
```

## Repo-Authored Cases

- `middle value missing`
- `one value missing from pair`
- `largest value missing`
- `zero missing`
- `one missing`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort and scan | `O(n log n)`. Sorting dominates the scan. | `O(1)`. The implementations sort the driver-isolated input in place. |
| 2 | Gauss sum | `O(n)`. The array is scanned once. | `O(1)`. Only sums are stored. |
| 3 | XOR | `O(n)`. Every index and value is processed once. | `O(1)`. Only one accumulator is stored. |

## Pitfalls

- The range includes both 0 and n, so there are n + 1 possible values.
- XOR works because every present value cancels with its index counterpart.
