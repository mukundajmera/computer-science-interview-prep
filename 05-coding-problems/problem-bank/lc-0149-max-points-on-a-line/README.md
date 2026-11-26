# Max Points on a Line

## Clean-Room Summary

Given point coordinates, return the largest number of points that lie on one straight line.

## Driver Signature

```java
class Solution {
    public int maxPoints(int[][] points) {
        // implementation
    }
}
```

```python
class Solution:
    def maxPoints(self, points: List[List[int]]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `points = [[0, 0], [2, 2], [3, 3], [0, 2]]` | `3` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Triple collinearity | `O(n^3)`. There are O(n^2) pairs and each pair scans all n points. | `O(1)`. Only counters and coordinate differences are stored. |
| 2 | Anchor slope map | `O(n^2)`. Each anchor compares against every other point once. | `O(n)`. The slope frequency map for one anchor can contain O(n) slopes. |

## Pitfalls

- Normalize slope signs so equivalent directions share one key.
- Vertical and horizontal lines need stable canonical representations.
- Use cross multiplication for the brute-force collinearity test to avoid floating-point errors.
