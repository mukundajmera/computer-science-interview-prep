# Combination Sum

## Clean-Room Summary

Return every nondecreasing combination of candidate numbers that sums to the target, allowing each candidate to be reused.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> combinationSum(int[] candidates, int target) {
        // implementation
    }
}
```

```python
class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `candidates = [3,4,5], target = 9` | `[[3,3,3],[4,5]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Include-current recursion | `O(R)`. The recursion explores candidate reuse branches up to the number of generated partial combinations R. | `O(R)`. The output stores all valid combinations and the recursion path stores one active combination. |
| 2 | Loop backtracking | `O(R)`. The search cost scales with the number of explored partial and complete combinations R. | `O(R)`. The output dominates; recursion depth is bounded by target divided by the smallest candidate. |

## Pitfalls

- Keep the start index fixed when reusing a candidate.
- Sort candidates to produce deterministic nondecreasing combinations.
- Stop exploring a branch once the remaining target would go negative.
