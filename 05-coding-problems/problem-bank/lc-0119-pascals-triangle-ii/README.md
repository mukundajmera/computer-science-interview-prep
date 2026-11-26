# Pascal's Triangle II

## Clean-Room Summary

Given an integer `rowIndex`, return the `rowIndex`-th (0-indexed) row of Pascal's triangle.

## Driver Signature

```java
class Solution {
    public List<Integer> getRow(int rowIndex) {
        // implementation
    }
}
```

```python
class Solution:
    def getRow(self, rowIndex: int) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `rowIndex = 3` | `[1,3,3,1]` |
| `rowIndex = 0` | `[1]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Single row in-place update | `O(k^2)`. Updating $k$ times across shrinking/expanding positions. | `O(k)`. Uses a single list of size $k + 1$. |

## Pitfalls

- Updating elements left-to-right would overwrite values needed for subsequent elements; updating backwards (right-to-left) preserves the prior row state.
- `rowIndex = 0` produces `[1]`.
