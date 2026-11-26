# Pattern: Graphs

## Theory
Graphs are versatile structures for modeling relationships. Graph algorithms such as BFS, DFS, Topological Sort (Kahn's), and Shortest Paths (Dijkstra's, Bellman-Ford) are fundamental to solving dependency, traversal, and routing problems.

### DAG (Directed Acyclic Graph)
A DAG has no cycles and is commonly used for dependencies (like course prerequisites).

```mermaid
graph TD
    A --> B
    A --> C
    B --> D
    C --> D
```

### Dijkstra Step
Dijkstra's algorithm finds the shortest path from a source to all other nodes in a graph with non-negative edge weights.

```mermaid
graph LR
    A((A: 0)) -- 1 --> B((B: 1))
    A -- 4 --> C((C: 4))
    B -- 2 --> C((C: 3))
    B -- 5 --> D((D: 6))
    C -- 1 --> D((D: 4))
```

## System Design Relevance
| Concept | Relevance |
|---------|-----------|
| Dependency Resolution | Agentic workflow orchestrator components like task dependencies and topological ordering. |
| Shortest Path | Network routing, delivery systems. |

## 🔗 Cross-links
- [Agentic Workflow Orchestrator](../../06-genai-systems/02-llm-hld-projects/agentic-workflow-orchestrator/)
