# Bus Routes

- Canonical ID: `lc-0815-bus-routes`
- Difficulty: `hard`
- Status: `verified`

## Clean-Room Problem Summary

Given bus routes as stop cycles, find the fewest buses needed to travel from a source stop to a target stop. Boarding any bus lets you reach every stop on that route.

## Driver Signature

- Java: `int numBusesToDestination(int[][] routes, int source, int target)`
- Python: `numBusesToDestination(routes: List[List[int]], source: int, target: int) -> int`

## Key Cases and Invariants

- Stops are graph nodes only indirectly; routes are often better BFS states.
- The source equal to target needs zero buses.
- Visited routes prevent repeatedly boarding the same bus through different stops.

## Solution Ladder

### Tier 1: Route BFS

Build stop-to-route membership, then BFS by route levels from every route serving the source stop.

- Time: `O(RS)` - Every route-stop membership is processed at most once.
- Space: `O(RS)` - The stop map stores route membership for every listed stop.

### Tier 2: Stop BFS

BFS over reachable stops while marking each route as boarded the first time it is expanded.

- Time: `O(RS)` - Each route is expanded once and contributes its stops once.
- Space: `O(RS)` - The stop map, queues, and visited sets are linear in route-stop entries.
