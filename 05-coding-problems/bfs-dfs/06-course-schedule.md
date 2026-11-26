# Course Schedule

## Overview

Given `numCourses` and prerequisite pairs, determine whether all courses can be finished.

This is directed-cycle detection. A course can be completed only if its prerequisite chain has no cycle.

## Requirements and constraints

- Courses are nodes.
- Prerequisite pairs are directed edges.
- Return a boolean for feasibility.
- Prefer `O(V + E)` time.

## Recognition cue

"Prerequisites", "dependencies", "can finish", and "cycle" point to a directed graph. Topological sort or DFS color marking are both valid.

## Invariant

For DFS color marking:

- `unvisited`: not explored yet.
- `visiting`: currently on the recursion path.
- `visited`: fully checked and cycle-free below this node.

Finding an edge to a `visiting` node proves a directed cycle.

## High-level design / approach

1. Build adjacency list from prerequisite to dependent course.
2. Initialize all nodes as unvisited.
3. DFS each unvisited course:
   - mark it visiting;
   - recursively check neighbors;
   - if a visiting neighbor appears, return false;
   - mark it visited.
4. If all DFS calls finish, return true.

## Dry run

Courses: `0,1,2`; prerequisites: `[1 requires 0]`, `[2 requires 1]`, `[0 requires 2]`.

| DFS node | Active path | Finding |
|---|---|---|
| `0` | `0` | go to `1` |
| `1` | `0 -> 1` | go to `2` |
| `2` | `0 -> 1 -> 2` | edge to `0`, which is visiting |

Answer: `false`.

## Language-neutral pseudocode

```text
build graph prereq -> course
state = array of unvisited

has_cycle(course):
    if state[course] == visiting: return true
    if state[course] == visited: return false
    state[course] = visiting
    for next in graph[course]:
        if has_cycle(next): return true
    state[course] = visited
    return false

for course in all courses:
    if has_cycle(course): return false
return true
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Edge direction | States and uses a consistent prerequisite direction |
| Cycle detection | Distinguishes active path from fully processed node |
| Disconnected graph | Checks every course, not only course `0` |
| Complexity | `O(V + E)` time and space |

## Common pitfalls

1. Treating the directed graph as undirected.
2. Using one boolean visited set and missing active-path cycles.
3. Reversing edge direction and confusing order output.
4. Forgetting isolated courses.

## Follow-up questions

1. How would you return a valid course order?
2. How would Kahn's algorithm solve the same problem?
3. How would you explain cycle detection in a deployment pipeline?

## Variants and extensions

- Course Schedule II.
- Build dependency ordering.
- Workflow DAG validation.

## Cross-links

- [BFS / DFS Overview](./01-overview.md)
- [Workflow Orchestration](../../03-hld-concepts/workflow-orchestration/THEORY.md)
- [Job Scheduler HLD](../../04-hld-projects/job-scheduler/)
