# Interleaving String

## Clean-Room Summary

Given two source strings and a target string, decide whether the target can be formed by taking every character from both sources while preserving the order inside each source.

## Driver Signature

```java
class Solution {
    public boolean isInterleave(String s1, String s2, String s3) {
        // implementation
    }
}
```

```python
class Solution:
    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `s1="abc", s2="def", s3="adbcef"` | `true` |
| `s1="abc", s2="def", s3="abdfec"` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Memoized DFS over source indices | `O(m*n)`. Each pair of consumed lengths is solved once. | `O(m*n)`. Memo entries and recursion depth store reachable states. |
| 2 | 2D reachability DP | `O(m*n)`. Every grid cell is evaluated from its top and left predecessors. | `O(m*n)`. The reachability table stores all prefix pairs. |
| 3 | 1D rolling DP | `O(m*n)`. The same transition is evaluated with one row of state. | `O(n)`. Only the shorter source dimension needs to remain in memory. |

## Pitfalls

- The target length must equal the combined source lengths.
- Characters can match both sources at a state; both transitions must be considered.
- Preserving order inside each source is stricter than matching a character multiset.
