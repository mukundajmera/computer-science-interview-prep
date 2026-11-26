# Alien Dictionary

## Clean-Room Summary

Infer a character ordering from a sorted word list; return an empty string when the ordering constraints are contradictory.

## Driver Signature

```java
class Solution {
    public String alienOrder(String[] words) {
        // implement
    }
}
```

```python
class Solution:
    def alienOrder(self, words: List[str]) -> str:
        # implement
```

## Repo-Authored Cases

- `single letter chain`
- `multi character unique chain`
- `invalid prefix order`
- `cycle is impossible`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS colors | `O(C + E)`. Each character and edge is processed once. | `O(C + E)`. The graph, color map, and output stack are stored. |
| 2 | Kahn topological sort | `O(C log C + E)`. Priority-queue operations keep deterministic output among zero-indegree characters. | `O(C + E)`. The graph, indegrees, and heap store characters and edges. |

## Pitfalls

- A longer word before its own prefix is invalid.
- These cases use unique valid orders because the catalog does not yet have an alien-order matcher.
