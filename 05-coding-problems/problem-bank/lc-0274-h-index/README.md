# H-Index

## Clean-Room Summary

Given citation counts for a researcher, return the largest h such that at least h papers have at least h citations each.

## Driver Signature

```java
class Solution {
    public int hIndex(int[] citations) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def hIndex(self, citations: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| citations | h-index |
|---|---:|
| `[4, 4, 0, 2, 8]` | `3` |
| `[0, 0, 1]` | `1` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort and count qualifying papers | `O(n log n)`. | `O(n)` conservative auxiliary bound for runtime sorting. |
| 2 | Counting buckets by capped citation count | `O(n)`. | `O(n)`. |

## Pitfalls

- The h-index is capped by the number of papers, not by the largest citation count.
- Counts greater than n can be grouped together for the bucket approach.
- The answer is the largest feasible h, so scanning direction matters.
