# Minimum Genetic Mutation

## Clean-Room Summary

Given a start gene, target gene, and allowed bank, return the minimum one-character mutations needed to reach the target or -1 if no valid path exists.

## Driver Signature

```java
class Solution {
    public int minMutation(String startGene, String endGene, String[] bank) {
        // implementation
    }
}
```

```python
class Solution:
    def minMutation(self, startGene: str, endGene: str, bank: List[str]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `startGene = "AAAAAAAA", endGene = "CCCCAAAA"` | `4` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | BFS bank scan | `O(B^2 L)`. For up to B bank genes, each BFS layer may compare against unused genes of length L. | `O(B)`. The queue and visited set can hold bank genes. |
| 2 | Generated-neighbor BFS | `O(BL)`. Each reachable bank gene generates a constant alphabet of L positions. | `O(B)`. The bank set, visited removals, and queue are linear in the number of bank genes. |

## Pitfalls

- Every intermediate gene must be in the bank.
- Only one character may change per mutation step.
- A visited set is required to avoid revisiting the same gene through longer paths.
