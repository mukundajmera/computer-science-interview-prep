# Backtracking Quiz

> 32 multiple-choice questions plus written drills to test recursive state, pruning, restore discipline, duplicate handling, board constraints, and system-design transfer.
>
> Time: 40 minutes | Difficulty: Intermediate

## Section 1: Pattern Recognition

### Question 1
Which prompt most strongly suggests backtracking?

A) Find the shortest path in an unweighted graph
B) Generate all valid subsets
C) Compute a rolling average
D) Merge two sorted arrays

### Question 2
What is the core backtracking loop?

A) Sort, scan, and commit permanently
B) Choose, validate, recurse, undo
C) Enqueue, dequeue, and mark by level
D) Split, memoize, and return a scalar

### Question 3
Which phrase is a strong recognition cue?

A) "all possible arrangements"
B) "nearest node"
C) "minimum edge weight"
D) "constant-time lookup"

### Question 4
When should plain backtracking be suspicious?

A) The prompt asks for all valid boards
B) The prompt asks for all permutations
C) The prompt has repeated subproblems and asks for only an optimal value
D) The prompt requires undoing mutable state

### Question 5
Which problem is a constraint-placement problem?

A) N-Queens
B) Binary Search
C) Two Sum
D) Merge Intervals

### Question 6
Which problem is grid path backtracking?

A) Word Search
B) Activity Selection
C) Best Time to Buy and Sell Stock
D) Meeting Rooms

### Question 7
Which problem uses prefix partition choices?

A) Palindrome Partitioning
B) Jump Game
C) Rotting Oranges
D) Clone Graph

### Question 8
What system-design problem most resembles bounded backtracking?

A) Trying dependency-safe resource placements under constraints
B) Reading a static CSS file
C) Returning an HTTP 404
D) Renaming a Markdown heading

## Section 2: Invariants and Mechanics

### Question 9
In Subsets, what does the recursive index represent?

A) The sum of chosen values
B) The next item whose include or exclude choice is undecided
C) The current graph depth from a source
D) The sorted rank of the answer

### Question 10
Why must a path be copied before adding it to results?

A) To sort the path
B) Because the mutable path will be changed by later undo operations
C) To reduce time complexity to `O(1)`
D) Because recursion cannot return arrays

### Question 11
In Permutations, what does `used` prevent?

A) Duplicating a value in the same permutation
B) Returning answers in any order
C) Visiting grid cells diagonally
D) Sorting the input

### Question 12
In Combination Sum, why use a `start` index?

A) To force combinations into a stable order and avoid permutation duplicates
B) To make every candidate single-use only
C) To compute shortest path distance
D) To detect cycles

### Question 13
For standard Combination Sum with reuse allowed, the recursive call usually uses:

A) `dfs(i, remaining - candidate)`
B) `dfs(0, target)` every time
C) `dfs(i - 1, remaining)`
D) BFS by layers

### Question 14
In Word Search, the visited set should be:

A) Global across all starts forever
B) Path-local and restored after exploring a branch
C) Unnecessary because grids have no cycles
D) Sorted before use

### Question 15
In Palindrome Partitioning, when can a prefix be added to the path?

A) Only when it is a palindrome
B) Whenever it is the longest remaining substring
C) Only after sorting characters
D) Only when it has even length

### Question 16
In N-Queens, which diagonal formulas are commonly tracked?

A) `row - col` and `row + col`
B) `row * col` and `row / col`
C) `row % 2` and `col % 2`
D) `min(row, col)` only

## Section 3: Complexity and Edge Cases

### Question 17
Subsets output size is:

A) `n`
B) `2^n`
C) `log n`
D) `n^2` always

### Question 18
Permutations output size is:

A) `n!`
B) `2n`
C) `n log n`
D) `1`

### Question 19
What is the worst-case Sudoku search shape with `E` empty cells?

A) `O(9^E)` before pruning
B) `O(E log E)`
C) `O(1)` because the board is fixed
D) `O(E)` always

### Question 20
Which state must be restored in N-Queens?

A) Board cell, occupied column, and both diagonal sets
B) Only the final answer count
C) The input length
D) The sorted order

### Question 21
What duplicate-handling technique is common after sorting candidates?

A) Skip equal candidates at the same recursion depth
B) Delete all equal values from the input silently
C) Use DFS colors
D) Use a queue only

### Question 22
What is a safe prune in standard Combination Sum with positive candidates?

A) Stop when the sorted candidate is greater than remaining target
B) Stop when path length is odd
C) Stop when candidate is smaller than target
D) Stop after the first candidate always

### Question 23
What is a Word Search base-case risk?

A) Accessing `word[index]` before checking `index == word.length`
B) Copying the board
C) Trying four directions
D) Returning false on mismatch

### Question 24
What should be said about recursion space?

A) It is always `O(1)`
B) It includes maximum recursion depth and active path state
C) It is larger than output in every case
D) It is unrelated to input size

## Section 4: System Design Transfer

### Question 25
What production risk resembles missing an undo step?

A) State leakage between candidate plans
B) Faster cache hits
C) Smaller logs
D) Better static routing

### Question 26
Why do production planners bound exhaustive search?

A) Complete search can exceed latency or compute budgets
B) Backtracking cannot express constraints
C) Search has no state
D) Undo steps are illegal

### Question 27
What is the production analogue of a constraint set?

A) A fast validity index for used resources, conflicts, or policy rules
B) A CSS class name
C) A Markdown heading
D) A random delay

### Question 28
Which validation signal fits a placement-search engine?

A) Number of hidden conflicts, timeout rate, and fallback usage
B) Number of vowels in a title
C) Static asset file size only
D) Number of commits

### Question 29
When can memoization be added to backtracking?

A) When different branches reach the same subproblem state
B) When every answer must be printed and states never repeat
C) Only for sorting algorithms
D) Never

### Question 30
What is a strong backtracking wrap-up phrase?

A) "My partial state is always valid, and every branch is undone before the next branch."
B) "Recursion makes it fast."
C) "I do not need a base case."
D) "I will mutate the board and hope it works."

### Question 31
What should a candidate do if the search space is too large?

A) Discuss pruning, memoization, bounds, heuristics, or a different pattern
B) Hide the complexity
C) Claim it is linear
D) Remove the base case

### Question 32
Which backtracking detail matters most for clean sibling branches?

A) Restore all mutated state after recursion
B) Sort every answer alphabetically
C) Use a global visited set for all branches
D) Avoid base cases

## Written Drills

### Drill A
Define the recursive state and invariant for Subsets.

### Drill B
Explain why Permutations needs a `used` set or equivalent swap boundary.

### Drill C
For Combination Sum, explain why `start` prevents duplicate ordering.

### Drill D
For Word Search, explain why visited cells must be restored after each branch.

### Drill E
For N-Queens, explain how column and diagonal sets prune invalid placements.

### Drill F
Explain how to present backtracking in a production planner with timeouts and fallback behavior.
