# Graph Algorithms Quiz - Answer Key

> **Detailed rationales for the 20 graph algorithm questions**

---

### Question 1
**Answer: B) It explores nodes in monotonically increasing order of distance from the source.**
Dijkstra's algorithm is a greedy algorithm that relies on the fact that if all edge weights are non-negative, the shortest path to a node is finalized the moment it is extracted from the priority queue. Exploring in monotonically increasing order ensures this. It does not simply rely on the absence of cycles (It relies on the absence of cycles to finish.), traverse level by level using a queue like BFS (It uses a queue to traverse level by level.), or relax edges randomly (It relaxes edges in a random order until convergence.).

### Question 2
**Answer: C) It may permanently finalize a node's distance before discovering a shorter path through a negative edge.**
Because Dijkstra greedily finalizes the shortest distance upon extraction, a subsequent negative edge from a 'longer' path might actually provide a shorter overall route to an already finalized node, breaking the core invariant. Dijkstra does not naturally enter an infinite loop (It enters an infinite loop.) or fail because the priority queue can't handle negatives (The priority queue cannot sort negative numbers.). Modifying it to a DAG (It requires modifying the graph to be a DAG first.) is a different algorithm entirely.

### Question 3
**Answer: D) By performing a V-th relaxation step; if any distance updates, a cycle exists.**
Bellman-Ford relaxes all edges V-1 times, which is sufficient to find the shortest path in any graph without negative cycles. If a V-th relaxation still yields shorter paths, it mathematically proves the existence of a negative cycle. Using a boolean array (By keeping track of visited nodes using a boolean array.) or Union-Find (By using a Union-Find data structure to find self-loops.) only detects cycles, not whether they are negative. Checking tree depth (By checking if the shortest path tree has depth > E.) is less direct than the standard V-th relaxation.

### Question 4
**Answer: C) Tarjan's Algorithm**
Tarjan's Algorithm uses a single DFS pass to assign discovery times and low-link values to efficiently group nodes into SCCs. Kruskal and Prim are for MSTs. Kahn's is for Topological Sorting. Prim's (Prim's Algorithm) and Kruskal's (Kruskal's Algorithm) find Minimum Spanning Trees, while Kahn's (Kahn's Algorithm) is for Topological Sorting, not SCCs.

### Question 5
**Answer: A) All nodes with an in-degree of 0.**
Kahn's algorithm operates by continually removing nodes with no incoming dependencies. Therefore, it must start by enqueuing all nodes that have an in-degree of exactly 0. Starting with a random node (A randomly selected node.), out-degree 0 nodes (All nodes with an out-degree of 0.), or max degree nodes (The node with the maximum degree.) would violate the dependency ordering fundamental to Topological Sort.

### Question 6
**Answer: B) After all of its outgoing neighbors have been fully explored.**
In DFS-based topological sort, a node is pushed to the stack only in the post-order step, after DFS has finished exploring all its descendants. This ensures dependencies are at the bottom of the stack. Adding nodes upon cycle detection (Whenever a cycle is detected.), when first visited (Immediately when it is first visited.), or only without incoming edges (Only if it has no incoming edges.) breaks the post-order requirement that guarantees dependencies are resolved.

### Question 7
**Answer: A) Disjoint Set Union (Union-Find)**
Kruskal's sorts all edges and adds them to the MST as long as they don't form a cycle. Union-Find is the optimal data structure to quickly check for and merge components (cycle detection). A Trie (Trie), Binary Indexed Tree (Binary Indexed Tree), or Monotonic Stack (Monotonic Stack) do not efficiently support the cycle detection and set merging required by Kruskal's.

### Question 8
**Answer: C) It builds the MST by maintaining a single growing tree and adding the cheapest edge to an unvisited node.**
Prim's algorithm grows a single tree starting from an arbitrary node, always picking the lowest-weight edge that connects a visited node to an unvisited node. Prim's is not always faster for sparse graphs (It is always faster than Kruskal's for sparse graphs.), does not sort edges first like Kruskal's (It sorts all edges first and adds them one by one if they don't form a cycle.), and can theoretically handle negative weights in some implementations, unlike the claim that it requires all positives (It requires all edge weights to be positive.).

### Question 9
**Answer: C) O(E log V)**
Using an adjacency list and a binary heap (priority queue), every edge is relaxed at most once (O(E)) and every extraction/insertion takes O(log V), resulting in O(E log V). The O(V E) (O(V E)), O(V^2 + E) (O(V^2 + E)), and O(V + E) (O(V + E)) bounds apply to different algorithms (like Bellman-Ford) or suboptimal implementations without a priority queue.

### Question 10
**Answer: C) Course scheduling with prerequisites to find an execution order.**
Topological sorting is the standard algorithm for determining a valid execution order in a Directed Acyclic Graph (DAG) of dependencies, like course scheduling. Negative weight cycles (Detecting negative weight cycles.), unweighted grid shortest paths (Finding the shortest path in an unweighted grid.), and maximum flow (Finding the maximum flow in a network.) require Bellman-Ford, BFS, and Ford-Fulkerson, respectively.

### Question 11
**Answer: A) The smallest node ID reachable from that node, including itself, using at most one back-edge.**
The low-link value tracks the earliest visited node reachable from a subtree. If a node's low-link value equals its own discovery time, it signifies the root of an SCC. The low-link does not track the number of incoming edges (The number of incoming edges to the node.), maximum out-degree (The maximum out-degree of any node in its component.), or DFS distance (The distance from the starting node of the DFS.).

### Question 12
**Answer: B) Floyd-Warshall is a dynamic programming approach that handles negative edges (but not cycles), whereas Dijkstra fails with negative edges.**
Floyd-Warshall computes all-pairs shortest paths using DP and correctly handles negative edge weights (provided no negative cycles), which breaks Dijkstra. Floyd-Warshall works on directed graphs (Floyd-Warshall only works on undirected graphs.), is slower on sparse graphs than Dijkstra (Floyd-Warshall is significantly faster on sparse graphs.), and can reconstruct paths via a predecessor matrix (Floyd-Warshall cannot reconstruct paths.).

### Question 13
**Answer: D) O(V^3)**
Floyd-Warshall relies on three nested loops over all vertices to check if going through an intermediate node `k` offers a shorter path between `i` and `j`, resulting in exactly O(V^3) operations. Complexities like O(V^2 E) (O(V^2 E)), O(E^2) (O(E^2)), and O(V E log V) (O(V E log V)) describe other paths algorithms or matrix multiplications, not the standard triple-loop DP.

### Question 14
**Answer: B) Assigning alternating colors (e.g., 0 and 1) to adjacent layers and checking for conflicts.**
A graph is bipartite if it can be colored with two colors such that no two adjacent nodes share a color. BFS processes the graph layer by layer, alternating colors. Finding an adjacent node with the same color proves it's not bipartite. A priority queue (Using a priority queue to sort by edge weight.), connected component counting (Counting the number of connected components.), or topological sorting (Running a topological sort and checking for cycles.) do not identify odd-length cycles which characterize non-bipartite graphs.

### Question 15
**Answer: A) Exactly two vertices have an odd degree.**
An Eulerian path traverses every edge exactly once. For a path (not a cycle) to exist, the graph must have exactly two nodes with an odd degree (the start and end nodes). If all nodes have an even degree, it's an Eulerian cycle. A graph can have cycles (The graph has no cycles.) and need not be a tree (The graph must be a tree.). If all vertices have an even degree (All vertices have an even degree.), it forms an Eulerian cycle, not just a path.

### Question 16
**Answer: A) A path that visits every vertex exactly once.**
A Hamiltonian path is a path in an undirected or directed graph that visits every vertex exactly once. Visiting every vertex and ending at the start (A path that visits every vertex and ends at the start.) is a Hamiltonian cycle. Using every edge exactly once (A path that uses every edge exactly once.) is an Eulerian path. Shortest path (The shortest path between two nodes.) is completely different.

### Question 17
**Answer: D) Path compression and union by rank/size.**
Path compression flattens the tree structure during `find`, and union by rank/size ensures the smaller tree is attached to the root of the larger one, keeping the tree shallow. Together, they yield the nearly constant amortized time complexity O(α(V)). Memoization (Memoization and bottom-up tabulation.), level-order traversal (Level-order traversal and hashing.), and adjacency matrix representations (Adjacency list and matrix representations.) are not optimizations for disjoint sets.

### Question 18
**Answer: D) The queue will eventually become empty before all nodes are processed, leaving nodes in the cycle unprocessed.**
Kahn's algorithm only enqueues nodes with an in-degree of 0. Nodes in a cycle will never reach an in-degree of 0, so the queue will empty prematurely, and the final topological sort count will be less than V, clearly indicating a cycle. It does not infinite loop or error out natively. It does not infinite loop (It will enter an infinite loop.), fail explicitly on cycle nodes while succeeding elsewhere (It will correctly output nodes that are not part of the cycle but fail on cycle nodes.), or throw a recursion depth error (It throws a recursion depth exceeded error.) since it is typically implemented iteratively with a queue.

### Question 19
**Answer: B) h(n) must never overestimate the true cost to reach the goal.**
An admissible heuristic is optimistic; it assumes the path to the goal is shorter than or equal to the actual path cost. If it overestimates, A* might settle for a sub-optimal path because it falsely believes the optimal path is too expensive. Exact equality (h(n) must be exactly equal to the true cost.), overestimating (h(n) must always overestimate the true cost.), or dynamic calculation based on past nodes (h(n) must be calculated dynamically based on past visited nodes.) violate the optimistic lower-bound requirement of admissibility.

### Question 20
**Answer: D) O(V E)**
Bellman-Ford iterates through all E edges V-1 times. Thus, its time complexity is literally O(V * E). Complexities like O(V + E) (O(V + E)), O(E log V) (O(E log V)), and O(V^2) (O(V^2)) belong to BFS, Dijkstra's, or dense graph algorithms.

