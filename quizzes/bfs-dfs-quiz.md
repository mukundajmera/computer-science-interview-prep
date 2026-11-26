# BFS / DFS Quiz

> 32 questions to test traversal choice, visited discipline, graph modeling, grid traversal, dependency cycles, and system-design transfer.
>
> Time: 40 minutes | Difficulty: Intermediate

## Section 1: Pattern Recognition

### Question 1
Which prompt most strongly suggests BFS?

A) Find all permutations
B) Find the shortest path in an unweighted graph
C) Sort an array in place
D) Count coin combinations

### Question 2
Which prompt most strongly suggests DFS?

A) Detect whether a directed dependency graph has a cycle
B) Find median of two sorted arrays
C) Maintain a rolling sum
D) Find first position in a sorted array

### Question 3
In Number of Islands, what are the graph nodes?

A) Water cells only
B) Rows only
C) Land cells
D) Columns only

### Question 4
Which phrase is a multi-source BFS signal?

A) "all subsets"
B) "sorted ascending"
C) "choose or skip"
D) "simultaneously spreads each minute"

### Question 5
When should plain BFS not be used for shortest path?

A) Unweighted edges
B) Weighted edges
C) Tree level order
D) Grid cells with unit moves

### Question 6
What does topological traversal require?

A) An undirected tree
B) A sorted array
C) A directed acyclic graph
D) A monotonic predicate

### Question 7
Which problem uses reverse reachability well?

A) Pacific Atlantic Water Flow
B) Classic Binary Search
C) House Robber
D) Search Insert Position

### Question 8
Which system design problem maps naturally to BFS frontier reasoning?

A) CSS color selection
B) Memoization table compression
C) SQL column naming
D) Web crawler frontier expansion

## Section 2: Invariants and Mechanics

### Question 9
Why mark a node visited before enqueueing in BFS?

A) To sort neighbors
B) To prevent duplicate queue entries
C) To make edges weighted
D) To skip the start node

### Question 10
What does a DFS `visiting` color mean in directed-cycle detection?

A) The node is fully processed
B) The node is disconnected
C) The node is on the active recursion path
D) The node has no neighbors

### Question 11
In tree level order traversal, why capture queue size at the start of a level?

A) To reverse the tree
B) To detect cycles
C) To sort values
D) To process exactly one level

### Question 12
In Clone Graph, why is an original-to-clone map required?

A) To avoid duplicate clones and preserve cycles
B) To make values unique
C) To remove all edges
D) To convert graph to a tree

### Question 13
What is the invariant in Word Ladder BFS?

A) DFS path is always shortest
B) First discovery gives shortest transformation distance
C) Every word has one neighbor
D) Dictionary lookup is sorted

### Question 14
What should Course Schedule return when it finds an edge to a `visiting` node?

A) True, all courses can finish
B) False, a cycle exists
C) The number of courses
D) The sorted order

### Question 15
For Number of Islands, why scan every cell?

A) BFS requires sorted rows
B) DFS cannot start from land
C) The graph may have disconnected components
D) Diagonal cells are always connected

### Question 16
What is the reversed condition in Pacific Atlantic search?

A) Move only to lower neighbors
B) Move diagonally only
C) Move to every cell regardless of height
D) Move from ocean inward to neighbors with height greater than or equal to current

## Section 3: Complexity and Edge Cases

### Question 17
Graph BFS/DFS usually costs:

A) `O(V + E)`
B) `O(log V)`
C) `O(V^2)` always
D) `O(1)`

### Question 18
Grid flood fill over `R x C` cells costs:

A) `O(log C)`
B) `O(R * C)`
C) `O(R + C)` always
D) `O(1)`

### Question 19
DFS auxiliary space includes:

A) Only output
B) No memory
C) Recursion stack or explicit stack
D) CPU cache only

### Question 20
What should Rotting Oranges return if fresh oranges remain unreachable?

A) `0`
B) Last queue size
C) Number of rotten oranges
D) `-1`

### Question 21
What is an edge case for Clone Graph?

A) Null input
B) Sorted matrix
C) Negative coin value
D) Empty dictionary only

### Question 22
What is a common Word Ladder off-by-one issue?

A) Using a queue
B) Counting sequence length vs edge count
C) Checking dictionary membership
D) Marking visited

### Question 23
Which statement is honest for binary tree level-order space?

A) `O(1)` always
B) `O(log n)` always
C) `O(w)` queue space, where `w` is maximum width
D) No auxiliary space

### Question 24
Why can recursive grid DFS be risky?

A) It cannot mark visited
B) It cannot inspect neighbors
C) It changes time complexity to `O(log n)`
D) It can exceed call-stack depth on huge components

## Section 4: System Design Transfer

### Question 25
How does BFS map to a web crawler?

A) Frontier queue of URLs by depth or priority layer
B) SQL normalization
C) DP table compression
D) Binary midpoint choice

### Question 26
What production risk resembles missing a visited set?

A) Faster index lookup
B) Duplicate crawling or replay loops
C) Lower memory usage always
D) Fewer retries

### Question 27
How does dependency-cycle detection map to systems?

A) Image resizing only
B) Cache TTL tuning only
C) Build pipelines and workflow DAG validation
D) CSS layout

### Question 28
What is the production equivalent of BFS frontier explosion?

A) Balanced binary search
B) O(1) cache lookup
C) Static route naming
D) Queue and memory growth from too many discovered tasks

### Question 29
When can bidirectional BFS help?

A) Shortest path with known start and target and large branching factor
B) Counting coin combinations
C) Sorting a nearly sorted array
D) Finding all subsets

### Question 30
Why is DFS color marking useful in orchestration systems?

A) It improves CSS specificity
B) It detects active dependency cycles before execution
C) It compresses arrays
D) It removes need for observability

### Question 31
What should a candidate say about input mutation in grid traversal?

A) Always mutate silently
B) Never use visited
C) State whether mutation is allowed; otherwise use a separate visited set
D) Only mutate water cells

### Question 32
What is the strongest BFS/DFS wrap-up?

A) "I use recursion because it is shorter."
B) "I use BFS for every graph problem."
C) "I ignore cycles unless tests fail."
D) "I model nodes and neighbors, choose BFS for layers/shortest unweighted paths or DFS for components/cycles, mark visited correctly, and account for frontier/stack space."
