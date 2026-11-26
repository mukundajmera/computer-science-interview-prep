# Cheapest Flights Within K Stops

## Clean-Room Summary

Find the cheapest directed route from source to destination while using at most k intermediate stops.

## Driver Signature

```java
class Solution {
    public int findCheapestPrice(int n, int[][] flights, int src, int dst, int k) {
        // implement
    }
}
```

```python
class Solution:
    def findCheapestPrice(self, n: int, flights: List[List[int]], src: int, dst: int, k: int) -> int:
        # implement
```

## Repo-Authored Cases

- `direct wins with one stop cap`
- `two stops allow chain`
- `unreachable destination`
- `cheaper route exceeds cap`
- `zero stop direct only`
- `zero stop without direct route`
- `exactly one stop cheaper`
- `too many stops rejected`
- `two stops unlock cheapest`
- `cycle does not trap search`
## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Limited Bellman-Ford | `O(KE)`. For K = k + 1 allowed flight edges, each layer scans every flight once. | `O(V)`. Only previous and current best-cost arrays are stored. |
| 2 | Stateful Dijkstra | `O((V + E)K log(VK))`. For K = k + 1 allowed flight edges, a city can have distinct useful costs per edge count. | `O(VK + E)`. The adjacency list, heap, and best table store per-stop states. |

## Pitfalls

- The stop limit means at most k + 1 flight edges, not k edges.
- A cheaper path to a city with too many used edges may be unusable for the destination.
