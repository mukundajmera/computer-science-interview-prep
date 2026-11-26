# Graph Algorithms Quiz

**Difficulty:** Advanced | **Time:** 45 minutes

20 coding-pattern questions for Dijkstra, Bellman-Ford, Topological Sort (Kahn vs DFS), Tarjan SCC, Kruskal and Prim MST algorithms.

### Question 1
Dijkstra's Algorithm relies on which property to guarantee correctness without negative weights?
- **A)** It relies on the absence of cycles to finish.
- **B)** It explores nodes in monotonically increasing order of distance from the source.
- **C)** It uses a queue to traverse level by level.
- **D)** It relaxes edges in a random order until convergence.

### Question 2
What is the primary failure condition for Dijkstra's Algorithm on a graph with negative edge weights?
- **A)** It enters an infinite loop.
- **B)** It requires modifying the graph to be a DAG first.
- **C)** It may permanently finalize a node's distance before discovering a shorter path through a negative edge.
- **D)** The priority queue cannot sort negative numbers.

### Question 3
How does Bellman-Ford detect a negative weight cycle?
- **A)** By keeping track of visited nodes using a boolean array.
- **B)** By using a Union-Find data structure to find self-loops.
- **C)** By checking if the shortest path tree has depth > E.
- **D)** By performing a V-th relaxation step; if any distance updates, a cycle exists.

### Question 4
Which algorithm is specifically designed to find Strongly Connected Components in a directed graph using a single DFS pass?
- **A)** Prim's Algorithm
- **B)** Kahn's Algorithm
- **C)** Tarjan's Algorithm
- **D)** Kruskal's Algorithm

### Question 5
In Kahn's Algorithm for Topological Sorting, what is the initial state of the queue?
- **A)** All nodes with an in-degree of 0.
- **B)** A randomly selected node.
- **C)** All nodes with an out-degree of 0.
- **D)** The node with the maximum degree.

### Question 6
When using DFS for Topological Sorting, when should a node be added to the result stack?
- **A)** Whenever a cycle is detected.
- **B)** After all of its outgoing neighbors have been fully explored.
- **C)** Immediately when it is first visited.
- **D)** Only if it has no incoming edges.

### Question 7
What data structure is essential for an optimal implementation of Kruskal's Minimum Spanning Tree algorithm?
- **A)** Disjoint Set Union (Union-Find)
- **B)** Trie
- **C)** Binary Indexed Tree
- **D)** Monotonic Stack

### Question 8
Which property is true for Prim's Algorithm?
- **A)** It is always faster than Kruskal's for sparse graphs.
- **B)** It sorts all edges first and adds them one by one if they don't form a cycle.
- **C)** It builds the MST by maintaining a single growing tree and adding the cheapest edge to an unvisited node.
- **D)** It requires all edge weights to be positive.

### Question 9
What is the time complexity of a standard priority-queue based Dijkstra's algorithm on a graph with V vertices and E edges?
- **A)** O(V E)
- **B)** O(V^2 + E)
- **C)** O(E log V)
- **D)** O(V + E)

### Question 10
Which of the following problems can be optimally solved using a standard Topological Sort?
- **A)** Detecting negative weight cycles.
- **B)** Finding the shortest path in an unweighted grid.
- **C)** Course scheduling with prerequisites to find an execution order.
- **D)** Finding the maximum flow in a network.

### Question 11
In Tarjan's SCC algorithm, what does the 'low-link' value of a node represent?
- **A)** The smallest node ID reachable from that node, including itself, using at most one back-edge.
- **B)** The number of incoming edges to the node.
- **C)** The maximum out-degree of any node in its component.
- **D)** The distance from the starting node of the DFS.

### Question 12
How does Floyd-Warshall differ from running Dijkstra from every node?
- **A)** Floyd-Warshall only works on undirected graphs.
- **B)** Floyd-Warshall is a dynamic programming approach that handles negative edges (but not cycles), whereas Dijkstra fails with negative edges.
- **C)** Floyd-Warshall is significantly faster on sparse graphs.
- **D)** Floyd-Warshall cannot reconstruct paths.

### Question 13
What is the time complexity of the Floyd-Warshall algorithm?
- **A)** O(V^2 E)
- **B)** O(E^2)
- **C)** O(V E log V)
- **D)** O(V^3)

### Question 14
In a bipartite graph check using BFS, what is the core mechanism?
- **A)** Using a priority queue to sort by edge weight.
- **B)** Assigning alternating colors (e.g., 0 and 1) to adjacent layers and checking for conflicts.
- **C)** Counting the number of connected components.
- **D)** Running a topological sort and checking for cycles.

### Question 15
What condition is necessary and sufficient for an undirected, connected graph to have an Eulerian path (but not cycle)?
- **A)** Exactly two vertices have an odd degree.
- **B)** The graph has no cycles.
- **C)** The graph must be a tree.
- **D)** All vertices have an even degree.

### Question 16
What is a Hamiltonian path?
- **A)** A path that visits every vertex exactly once.
- **B)** A path that visits every vertex and ends at the start.
- **C)** A path that uses every edge exactly once.
- **D)** The shortest path between two nodes.

### Question 17
When implementing an optimal Union-Find for Kruskal's algorithm, what two optimizations are critical?
- **A)** Memoization and bottom-up tabulation.
- **B)** Level-order traversal and hashing.
- **C)** Adjacency list and matrix representations.
- **D)** Path compression and union by rank/size.

### Question 18
What happens if you run Kahn's algorithm on a directed graph that contains a cycle?
- **A)** It will enter an infinite loop.
- **B)** It will correctly output nodes that are not part of the cycle but fail on cycle nodes.
- **C)** It throws a recursion depth exceeded error.
- **D)** The queue will eventually become empty before all nodes are processed, leaving nodes in the cycle unprocessed.

### Question 19
In A* search, the heuristic function h(n) must be 'admissible' to guarantee shortest paths. What does this mean?
- **A)** h(n) must be exactly equal to the true cost.
- **B)** h(n) must never overestimate the true cost to reach the goal.
- **C)** h(n) must always overestimate the true cost.
- **D)** h(n) must be calculated dynamically based on past visited nodes.

### Question 20
What is the time complexity of Bellman-Ford algorithm?
- **A)** O(V + E)
- **B)** O(E log V)
- **C)** O(V^2)
- **D)** O(V E)
