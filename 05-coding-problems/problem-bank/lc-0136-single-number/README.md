# Single Number

## Clean-Room Summary

Given values where every value except one appears twice, return the value that appears once.

## Driver Signature

```java
class Solution {
    public int singleNumber(int[] nums) {
        // implementation
    }
}
```

```python
class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums = [9, 4, 9]` | `4` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Set cancellation | `O(n)`. Each array value performs one average-case set operation. | `O(n)`. The set can hold up to half of the array values before cancellations finish. |
| 2 | XOR cancellation | `O(n)`. The array is scanned once. | `O(1)`. Only one accumulator is maintained. |

## Pitfalls

- The input guarantee means cancellation is safe; no frequency validation is required.
- XOR works for negative values as well as positive values in both languages.
- A set-based solution is simpler but uses extra space.
