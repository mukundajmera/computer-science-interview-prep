# Union-Find Quiz

> 32 multiple-choice questions plus written drills to test DSU recognition, parent/rank invariants, component counting, cycle detection, identity merging, equality constraints, and system-design transfer.
>
> Time: 40 minutes | Difficulty: Intermediate

## Section 1: Pattern Recognition

### Question 1
What problem shape most strongly suggests Union-Find?

A) Undirected component merging and connectivity checks
B) Prefix autocomplete
C) Sliding time windows
D) Sorting all values once

### Question 2
What does `find(x)` return?

A) The shortest path from `x`
B) The representative root of `x`'s component
C) The next lexicographic word
D) The median value

### Question 3
What does `union(a, b)` do when roots differ?

A) Deletes an edge
B) Finds a directed path
C) Merges two components
D) Sorts a component

### Question 4
Which problem is a canonical DSU component counter?

A) Word Dictionary wildcard search
B) Sliding Window Maximum
C) Koko Eating Bananas
D) Number of Connected Components

### Question 5
Which valid-tree condition is required besides no cycle?

A) Exactly `n - 1` edges
B) Every node has degree two
C) Edges must be directed
D) Values must be sorted

### Question 6
In Redundant Connection, what indicates the redundant edge?

A) It contains the largest node id
B) Its endpoints already share a root
C) It appears first in the input
D) Its endpoints are different

### Question 7
Accounts Merge should merge accounts by:

A) Same display name only
B) Number of emails only
C) Shared email connectivity
D) Lexicographic account order only

### Question 8
Equality equations should be processed:

A) Inequalities first, equalities second
B) In random order without DSU
C) Only after sorting variables by rank
D) Equalities first, inequalities second

## Section 2: Invariants and State

### Question 9
When are two nodes connected in DSU?

A) `find(a) == find(b)`
B) `parent[a] == b` only
C) They appear in the same input line
D) Their values are adjacent

### Question 10
What does path compression do?

A) Deletes components
B) Rewrites visited nodes to point closer to the root
C) Sorts edges
D) Converts directed edges to undirected

### Question 11
What does union by rank or size prevent?

A) Duplicate strings
B) Prefix collisions
C) Tall parent trees
D) Matrix scanning

### Question 12
When should component count decrement?

A) On every edge
B) On every find call
C) Never
D) Only when union merges two different roots

### Question 13
In Graph Valid Tree, why does a same-root edge fail?

A) It creates an undirected cycle
B) It proves the graph is disconnected
C) It sorts the tree
D) It removes an isolated node

### Question 14
In Accounts Merge, why map emails to ids?

A) Emails cannot be compared
B) DSU parent arrays or maps need stable keys for each email
C) Names are always unique
D) Sorting is impossible

### Question 15
For Most Stones Removed, why encode rows and columns differently?

A) To sort stones by row
B) To make all stones isolated
C) To avoid row id and column id collisions
D) To avoid using DSU

### Question 16
For equality satisfiability, what makes `a!=b` impossible?

A) `a` and `b` are different letters
B) The equation appears late
C) There are more equalities than inequalities
D) `a` and `b` have the same root after equality unions

## Section 3: Complexity and Edge Cases

### Question 17
With path compression and union by rank, DSU operations are commonly described as:

A) Near-constant amortized, `O(alpha(n))`
B) Always `O(n^2)`
C) Always `O(log n!)`
D) Impossible to analyze

### Question 18
What is a common component-count bug?

A) Initializing count to `n`
B) Decrementing count for duplicate edges
C) Calling union on edges
D) Handling isolated nodes

### Question 19
Why is Union-Find not enough for shortest path?

A) It cannot store parents
B) It cannot process edges
C) It only knows component identity, not path length
D) It only works on strings

### Question 20
What graph type is usually not a direct DSU fit for reachability?

A) Undirected graph
B) Static component graph
C) Identity graph
D) Directed graph

### Question 21
For Number of Provinces, what cost usually dominates?

A) Scanning the `n x n` matrix
B) Sorting output strings
C) Prefix traversal
D) Heap pop cost

### Question 22
In Accounts Merge, what should happen before grouping emails?

A) Group by stale parent values directly
B) Call `find` after all unions to get final roots
C) Merge by name only
D) Remove all single-email accounts

### Question 23
For Most Stones Removed, answer equals:

A) number of rows plus columns
B) number of isolated coordinates
C) number of stones minus number of connected components
D) number of duplicate edges

### Question 24
What online update is hard for basic Union-Find?

A) Edge addition
B) Same-component query
C) Component count after union
D) Edge deletion

## Section 4: System Design Transfer

### Question 25
What production use maps well to Union-Find?

A) Identity merge or duplicate cluster construction
B) Autocomplete ranking only
C) Rendering CSS
D) Local string reversal

### Question 26
What does Union-Find provide in a graph-backed system?

A) Exact shortest path
B) Fast component identity for batch or append-only grouping
C) Full audit trail automatically
D) Directed reachability

### Question 27
What extra concern appears in production identity merges?

A) Alphabet size only
B) Heap tie-breakers only
C) Explainability and rollback of bad merges
D) Board neighbor order only

### Question 28
What metric validates a clustering pipeline?

A) Number of trie children
B) CSS bundle size
C) Median query only
D) Merge precision/recall or false-merge audit rate

### Question 29
When should a system choose graph traversal over DSU?

A) When it needs paths, neighborhoods, or directed reachability
B) Whenever it sees an undirected edge
C) Whenever components are static
D) Whenever items are strings

### Question 30
What is a DSU rollback use case?

A) Autocomplete typo correction
B) Offline dynamic connectivity with time-bounded changes
C) Full-text relevance
D) Sorting a static array

### Question 31
What should a candidate clarify when keys are strings?

A) Whether strings can be added to a heap
B) Whether all strings are prefixes
C) How strings map to stable DSU ids
D) Whether the graph is weighted

### Question 32
What is the best concise wrap-up for Union-Find problems?

A) Always run DFS on every query
B) Always store every path
C) Ignore isolated nodes
D) Define parent/rank, compress paths, merge different roots, and state DSU limits

## Written Drills

A. Explain why count decrements only on successful union.
B. Prove the valid-tree edge-count shortcut.
C. Walk through redundant connection detection.
D. Explain Accounts Merge id mapping and output reconstruction.
E. Explain the row/column DSU model for stones.
F. Translate Union-Find into a production identity-merge design.
