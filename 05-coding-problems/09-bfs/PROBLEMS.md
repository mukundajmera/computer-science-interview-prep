# Breadth-First Search Problems

## 1. Binary Tree Level Order Traversal

**Summary:** Visit a binary tree's nodes row by row, from top to bottom, returning each row's values.
**Practice:** [lc-0102-binary-tree-level-order-traversal](../problem-bank/lc-0102-binary-tree-level-order-traversal/README.md)

### Hints
1. Use a queue to keep track of nodes at the current level.
2. The number of elements in the queue at the start of a loop represents the size of the current level.
3. Dequeue that exact number of elements to form a level array, enqueuing their children for the next level.

### Complexity
- **Time:** O(N) where N is the number of nodes.
- **Space:** O(N) since the queue will hold at most N/2 nodes (the leaves in a balanced tree).

---

## 2. Minimum Depth of Binary Tree

**Summary:** Find the number of nodes on the shortest path from the root to any leaf.

### Hints
1. While DFS can solve this, BFS guarantees you find the shortest path first.
2. Return the current depth the moment you dequeue a node with no left and no right child.
3. Ensure you handle the case where the tree is empty.

### Complexity
- **Time:** O(N) in the worst case (e.g., a degenerate tree), but often faster since it early-exits on the first leaf.
- **Space:** O(N) for the queue.

---

## 3. Binary Tree Right Side View

**Summary:** List the values you would see looking at a binary tree from its right side, one per depth.
**Practice:** [lc-0199-binary-tree-right-side-view](../problem-bank/lc-0199-binary-tree-right-side-view/README.md)

### Hints
1. Perform a standard level-order traversal using a queue.
2. At each level, capture the value of the very last node processed in that loop.
3. Append this last node's value to your result list.

### Complexity
- **Time:** O(N) where N is the number of nodes.
- **Space:** O(N) for the queue.

---

## 4. Number of Islands

**Summary:** Count the separate groups of connected land cells in a grid of land and water.
**Practice:** [lc-0200-number-of-islands](../problem-bank/lc-0200-number-of-islands/README.md)

### Hints
1. Iterate over every cell. When you find a `'1'`, increment your island count and start a BFS.
2. During the BFS, mark visited cells by turning the `'1'` into a `'0'` (or use a visited set).
3. Enqueue all valid horizontal and vertical neighbors of land cells.

### Complexity
- **Time:** O(M * N) where M is rows and N is columns.
- **Space:** O(min(M, N)) which is the maximum queue size for BFS on a grid.

---

## 5. Rotting Oranges

**Summary:** Rot spreads between adjacent grid cells each minute; find how long until all fresh oranges rot, or that some never will.
**Practice:** [lc-0994-rotting-oranges](../problem-bank/lc-0994-rotting-oranges/README.md)

### Hints
1. This is a multi-source BFS problem. Enqueue all initially rotten oranges with depth (minute) 0.
2. Keep a count of fresh oranges. Decrement it every time a fresh orange rots.
3. At the end of the BFS, if the fresh count is > 0, return -1. Otherwise, return the max minutes tracked.

### Complexity
- **Time:** O(M * N)
- **Space:** O(M * N) for the queue.

---

## 6. Shortest Path in Binary Matrix

**Summary:** Find the length of the shortest eight-direction path through open cells from the top-left to the bottom-right.

### Hints
1. Before starting BFS, ensure the start cell and target cell are not blocked (i.e., not `1`).
2. Explore 8 possible directions. Since you need the shortest path, BFS is ideal.
3. Track the distance in the queue alongside the coordinates, or mutate the grid to store distances.

### Complexity
- **Time:** O(N^2) where N is the grid dimension.
- **Space:** O(N^2) for the queue.

---

## 7. Word Ladder

**Summary:** Find the shortest chain of single-letter changes from one word to another, using only dictionary words.
**Practice:** [lc-0127-word-ladder](../problem-bank/lc-0127-word-ladder/README.md)

### Hints
1. Model this as an unweighted graph where words are nodes, and edges exist if they differ by one character.
2. To find neighbors quickly, either mutate each character of the current word from 'a' to 'z' and check if it exists in a word set.
3. Keep track of levels (sequence length). Remove visited words from the set to prevent cycles and redundant work.

### Complexity
- **Time:** O(M^2 * N) where M is word length and N is the number of words in the list.
- **Space:** O(M^2 * N) for the graph/queue representation.

---

## 8. Course Schedule

**Summary:** Courses have prerequisite pairs; decide whether all courses can be completed without a circular dependency.
**Practice:** [lc-0207-course-schedule](../problem-bank/lc-0207-course-schedule/README.md)

### Hints
1. This is a topological sort problem that can be solved with Kahn's Algorithm (BFS).
2. Compute the in-degree of every node (course). A course with 0 in-degree has no prerequisites.
3. Enqueue all 0 in-degree nodes. As you process a node, decrement the in-degree of its neighbors. If a neighbor reaches 0 in-degree, enqueue it. Count processed nodes.

### Complexity
- **Time:** O(V + E) where V is `numCourses` and E is the number of dependencies.
- **Space:** O(V + E) to store the adjacency list and in-degrees.
