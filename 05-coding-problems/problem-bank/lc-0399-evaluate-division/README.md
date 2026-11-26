# Evaluate Division

## Clean-Room Summary

Given ratio facts between named variables, answer ratio queries by combining known relationships or returning `-1.0` when no relationship can be derived.

## Driver Signature

```java
class Solution {
    public double[] calcEquation(List<List<String>> equations, double[] values, List<List<String>> queries) {
        return new double[0];
    }
}
```

```python
class Solution:
    def calcEquation(self, equations: List[List[str]], values: List[float], queries: List[List[str]]) -> List[float]:
        return []
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| ratios `red/blue=2`, `blue/green=4`; queries `red/green`, `green/red`, `red/black` | `[8.0, 0.125, -1.0]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Weighted graph DFS per query | `O(q * (v + e))`. Each query may search a whole component. | `O(v + e)`. Store adjacency plus visited state. |
| 2 | Weighted union find | `O((e + q) * alpha(v))` amortized. Each union/find is near constant time. | `O(v)`. Store parent and ratio-to-parent maps. |

## Pitfalls

- A variable divided by itself is `1.0` only when the variable is known.
- Each equation must add both forward and reciprocal edges or equivalent union-find weights.
- Disconnected components and unknown variables should return `-1.0`.
