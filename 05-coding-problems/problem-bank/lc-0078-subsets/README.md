# Subsets

## Clean-Room Summary

Return every subset of the distinct input values, including the empty subset and the full set.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> subsets(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        # implement
```

## Repo-Authored Cases

- `three values`
- `single value`
- `empty input`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Bitmask enumeration | `O(n2^n)`. There are 2^n masks and each can inspect n positions. | `O(n2^n)`. The output contains 2^n subsets with up to n values each. |
| 2 | Backtracking include/exclude | `O(n2^n)`. Each subset copy can contain up to n values. | `O(n2^n)`. The output dominates; the decision path uses O(n) extra stack space. |

## Pitfalls

- Include the empty subset.
- Input values are distinct for this problem, so duplicate-skipping is not needed.
- Output order is flexible; the repo uses unordered nested-list matching.
