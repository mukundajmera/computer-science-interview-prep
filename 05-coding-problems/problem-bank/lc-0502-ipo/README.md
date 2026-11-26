# IPO

## Clean-Room Summary

Choose up to k affordable projects to maximize capital, where finishing a project immediately adds its profit.

## Driver Signature

```java
class Solution {
    public int findMaximizedCapital(int k, int w, int[] profits, int[] capital) {
        // implementation
    }
}
```

```python
class Solution:
    def findMaximizedCapital(self, k: int, w: int, profits: List[int], capital: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `k = 2, w = 1, profits = [2, 4, 3], capital = [0, 2, 1]` | `8` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Repeated scan | `O(kn)`. Each of up to k selections scans all n projects. | `O(n)`. A used marker tracks projects that have already been selected. |
| 2 | Capital sort profit heap | `O(n log n + k log n)`. Sorting costs n log n and each project enters the heap once; each selection pops one profit. | `O(n)`. The sorted project list and heap can store n projects. |

## Pitfalls

- Stop early when no affordable project remains.
- Use a max-heap for profit after filtering by capital.
- A project can be selected at most once.
