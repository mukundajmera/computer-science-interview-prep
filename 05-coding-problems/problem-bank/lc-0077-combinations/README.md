# Combinations

## Clean-Room Summary

Return every size-k subset of the numbers from 1 through n.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> combine(int n, int k) {
        // implementation
    }
}
```

```python
class Solution:
    def combine(self, n: int, k: int) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `n = 5, k = 2` | `[[1, 2], [1, 3], [1, 4], [1, 5], [2, 3], [2, 4], [2, 5], [3, 4], [3, 5], [4, 5]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Basic backtracking | `O(C(n,k) k)`. There are C(n,k) combinations and each stored result copies k numbers. | `O(C(n,k) k)`. The output stores every combination; the recursion path adds O(k). |
| 2 | Pruned backtracking | `O(C(n,k) k)`. The same C(n,k) results must be emitted and copied. | `O(C(n,k) k)`. The output dominates; the path and stack use O(k). |

## Pitfalls

- Prune start values that cannot leave enough remaining numbers.
- Copy the current path before storing it in the result.
- The numbers are one-indexed, not zero-indexed.
