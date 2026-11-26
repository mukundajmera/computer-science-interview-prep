# Permutations

## Clean-Room Summary

Return every ordering of the distinct input values.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> permute(int[] nums) {
        // implementation
    }
}
```

```python
class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums = [2,4,6]` | `[[2, 4, 6], [2, 6, 4], [4, 2, 6], [4, 6, 2], [6, 2, 4], [6, 4, 2]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Used-array backtracking | `O(n! n)`. There are n! permutations and each result copies n values. | `O(n! n)`. The output dominates; path and used flags use O(n). |
| 2 | In-place swaps | `O(n! n)`. All n! permutations are emitted and copied. | `O(n! n)`. The output dominates; recursion depth is O(n). |

## Pitfalls

- The input values are distinct, so no duplicate-skip logic is needed.
- Copy the current permutation before storing it.
- Swap-based generation must restore the array before returning.
