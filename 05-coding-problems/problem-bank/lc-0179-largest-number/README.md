# Largest Number

## Clean-Room Summary

Arrange non-negative integers so their decimal strings concatenate into the largest possible number.

## Driver Signature

```java
class Solution {
    public String largestNumber(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def largestNumber(self, nums: List[int]) -> str:
        # implement
```

## Repo-Authored Cases

- `two numbers`
- `multiple prefixes`
- `all zeroes collapse`
- `shared prefix order`
- `long shared prefix`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Exhaustive permutations | `O(n! * d)`. Every permutation is materialized and compared, with d total digits. | `O(n + d)`. The recursion path and candidate string are stored. |
| 2 | Concatenation sort | `O(n log n * d)`. Sorting performs comparator calls that compare concatenations of digit strings. | `O(n + d)`. String copies and the final concatenation are stored. |

## Pitfalls

- Numeric sort is wrong for prefix pairs such as 12 and 121.
- If the largest sorted value is 0, the whole answer should be exactly "0".
