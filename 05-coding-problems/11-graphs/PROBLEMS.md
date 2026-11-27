# Graph Problems

## 1. Course Schedule

**Summary:** Courses have prerequisite pairs; decide whether all courses can be completed without a circular dependency.
**Practice:** [lc-0207-course-schedule](../problem-bank/lc-0207-course-schedule/README.md)

**Hints**:
1. Build an adjacency list and an in-degree array.
2. Use Kahn's algorithm (BFS with a queue) to process courses with zero in-degree.
3. If the count of processed courses equals `numCourses`, return true.

**Complexity**: Time `O(V + E)`, Space `O(V + E)`

## 2. Course Schedule II

**Summary:** Produce an order in which all courses can be taken respecting prerequisites, or nothing if a cycle exists.
**Practice:** [lc-0210-course-schedule-ii](../problem-bank/lc-0210-course-schedule-ii/README.md)

**Hints**:
1. Similar to Course Schedule, but record the courses as they are processed.
2. If cycle exists, return empty.
3. Can also be solved using DFS with post-order traversal and reversal.

**Complexity**: Time `O(V + E)`, Space `O(V + E)`

## 3. Graph Valid Tree

**Summary:** Decide whether a set of undirected edges over n nodes forms a single tree.
**Practice:** [lc-0261-graph-valid-tree](../problem-bank/lc-0261-graph-valid-tree/README.md)

**Hints**:
1. A valid tree has exactly `n-1` edges.
2. The graph must be fully connected.
3. Check connectivity using DFS, BFS, or Union-Find.

**Complexity**: Time `O(V + E)`, Space `O(V + E)`

## 4. Alien Dictionary

**Summary:** Given words sorted by an unknown alphabet, recover one valid ordering of the letters, or report that none exists.
**Practice:** [lc-0269-alien-dictionary](../problem-bank/lc-0269-alien-dictionary/README.md)

**Hints**:
1. Compare adjacent words to find the first differing character to form a directed edge.
2. Perform topological sort.
3. If a cycle is detected, return empty string.

**Complexity**: Time `O(C)`, Space `O(1)` where C is total characters in words.

## 5. Network Delay Time

**Summary:** A signal spreads through a weighted directed network from a source; find when every node has received it.

**Hints**:
1. Use Dijkstra's algorithm to find the shortest paths from `k`.
2. Keep track of the maximum distance to any node.
3. If some node is unreachable, return -1.

**Complexity**: Time `O((V + E) log V)`, Space `O(V + E)`

## 6. Cheapest Flights Within K Stops

**Summary:** Find the cheapest route between two cities that uses at most a given number of intermediate stops.
**Practice:** [lc-0787-cheapest-flights-within-k-stops](../problem-bank/lc-0787-cheapest-flights-within-k-stops/README.md)

**Hints**:
1. Use Bellman-Ford algorithm with `k+1` iterations.
2. Alternatively, use Dijkstra with state `(cost, node, stops)`.
3. Keep track of minimum cost per node per stop.

**Complexity**: Time `O(E * K)`, Space `O(V)`

## 7. Min Cost to Connect All Points

**Summary:** Connect points on a plane with the least total Manhattan-distance cost so every point is reachable.

**Hints**:
1. This is a Minimum Spanning Tree (MST) problem.
2. Use Prim's algorithm with a min-heap or Kruskal's with Union-Find.
3. Compute distances on the fly to save space if needed.

**Complexity**: Time `O(V^2 log V)`, Space `O(V^2)`
