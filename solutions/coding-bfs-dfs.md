# Coach Answer: Coding BFS / DFS Pack

> Type: Coding Pattern Drill
> Difficulty: Intermediate
> Time Target: 45 minutes

## Phase 1 - Problem Framing

Strong candidates do not start with a queue or recursive function. They first define the graph.

1. Name the nodes: tree nodes, grid cells, courses, words, URLs, or states.
2. Name the neighbor function.
3. Decide whether edges are directed, undirected, weighted, or implicit.
4. Decide what counts as visited.
5. Choose BFS for shortest unweighted distance or layers; choose DFS for components, paths, cycles, and postorder.

## Phase 2 - Canonical Templates

### Template A: BFS

```text
queue = [start]
visited = {start}
while queue:
    node = queue.pop_front()
    for next in neighbors(node):
        if next not in visited:
            visited.add(next)
            queue.push_back(next)
```

Use for level order, shortest unweighted path, and spreading processes.

### Template B: DFS

```text
dfs(node):
    mark node visited
    for next in neighbors(node):
        if next not visited:
            dfs(next)
```

Use for components, exhaustive region traversal, and tree path problems.

### Template C: Directed Cycle Detection

```text
dfs(node):
    if state[node] == visiting: return cycle
    if state[node] == visited: return no_cycle
    state[node] = visiting
    for next in graph[node]:
        if dfs(next) finds cycle: return cycle
    state[node] = visited
    return no_cycle
```

The active recursion path matters. A node that is fully processed is safe to reuse.

### Template D: Multi-Source BFS

```text
queue = all starting sources at time 0
while queue:
    node, time = queue.pop_front()
    for next in neighbors(node):
        if next is fresh:
            mark next reached
            queue.push_back(next, time + 1)
```

All sources start together. Do not run one BFS per source.

## Phase 3 - Problem-by-Problem Walkthrough

1. **Binary Tree Level Order**
   - Capture queue size at level start.
   - Space is maximum width, not constant.

2. **Number of Islands**
   - Scan all cells.
   - Start traversal only from unvisited land.
   - Count once per component root.

3. **Clone Graph**
   - Original-to-clone map is the core.
   - Traversal order is secondary.

4. **Rotting Oranges**
   - Multi-source BFS from all rotten oranges.
   - Minutes are BFS layers.

5. **Course Schedule**
   - Directed-cycle detection using color states or Kahn's algorithm.
   - A boolean visited set alone is not enough.

6. **Word Ladder**
   - Shortest unweighted path over an implicit word graph.
   - Mark words visited before enqueue.

7. **Pacific Atlantic Water Flow**
   - Reverse the search from oceans.
   - Move uphill in reverse search.

## Phase 4 - Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Graph model | 20% | Defines nodes, neighbors, direction, and state |
| Traversal choice | 20% | Justifies BFS vs DFS from prompt requirements |
| Visited discipline | 25% | Prevents cycles, duplicate queue growth, and repeated states |
| Edge cases | 15% | Covers empty input, disconnected components, unreachable targets, and stack depth |
| Complexity | 10% | States `O(V + E)` or grid equivalent with real auxiliary space |
| Communication | 10% | Narrates invariant and production transfer clearly |

## Phase 5 - Common Pitfalls

1. Using DFS for unweighted shortest path.
2. Marking visited too late.
3. Missing disconnected components.
4. Ignoring directed cycle active-path state.
5. Counting BFS levels incorrectly.
6. Silently mutating grid input.
7. Hiding recursion stack space.
8. Building all implicit edges when on-the-fly neighbors are cheaper.

## System Design Transfer Script

Use this table to turn a coding answer into an architecture answer without sounding generic.

| Coding invariant | Production analogue | Scale risk | Validation signal |
|---|---|---|---|
| Frontier plus visited set bounds graph expansion | Web crawler frontier queue plus URL dedupe store | Queue explosion, duplicate fetches, crawl traps | Queue depth, dedupe hit rate, per-domain crawl freshness |
| Directed active-path cycle detection rejects back edges | Workflow DAG or build dependency validator | Invalid deploy order, cyclic job graph, deadlock-like waits | Cycle-reject rate, DAG compile success rate, blocked-node count |
| Multi-source BFS preserves simultaneous time layers | Incident blast-radius or propagation simulation | Incorrect time ordering hides real spread speed | Layer counts, max frontier width, replayed incident timeline |
| Reverse reachability starts from terminal sinks | Data-flow lineage, policy reachability, boundary analysis | Per-source traversal is too expensive | Reachability set size, stale edge count, recomputation time |

## Follow-Up Drill Set

1. Binary Tree Right Side View.
2. Max Area of Island.
3. Surrounded Regions.
4. Course Schedule II.
5. Walls and Gates.
6. Open the Lock.
7. Shortest Path in Binary Matrix.
8. Alien Dictionary.

## Cross-links

- [BFS / DFS Pattern Pack](../05-coding-problems/bfs-dfs/README.md)
- [BFS / DFS Quiz](../quizzes/bfs-dfs-quiz.md)
- [BFS / DFS Flashcards](../flashcards/bfs-dfs.md)
- [Web Crawler HLD](../04-hld-projects/web-crawler/)
- [Workflow Orchestration](../03-hld-concepts/workflow-orchestration/THEORY.md)
