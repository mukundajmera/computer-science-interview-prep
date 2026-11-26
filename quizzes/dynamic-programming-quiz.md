# Dynamic Programming Quiz

> 32 questions to test DP state definition, recurrence design, base cases, table order, space compression, and system-design transfer.
>
> Time: 45 minutes | Difficulty: Intermediate

## Section 1: Pattern Recognition

### Question 1
Which signal most strongly suggests dynamic programming?

A) Repeated overlapping subproblems with an optimization/count/feasibility objective
B) One midpoint discards half the array
C) Need to traverse all graph edges once
D) Need to generate every permutation

### Question 2
What should be defined before writing DP code?

A) Variable names only
B) State meaning
C) CSS layout
D) Test runner command only

### Question 3
Which phrase often indicates sequence DP?

A) "level order"
B) "first sorted position"
C) "longest common subsequence"
D) "connected island"

### Question 4
Which phrase indicates grid DP?

A) "shortest unweighted path"
B) "clone a graph"
C) "rotated sorted array"
D) "paths from top-left to bottom-right with right/down moves"

### Question 5
Why is Coin Change usually DP instead of greedy?

A) Coins are sorted
B) Some coin systems make local largest choice suboptimal
C) BFS always fails
D) The answer is always one coin

### Question 6
What distinguishes subsequence from substring?

A) Subsequence must be sorted
B) Substring may skip characters
C) Subsequence may skip characters; substring is contiguous
D) They are identical

### Question 7
Which DP objective is Word Break?

A) Minimum cost
B) Maximum value
C) Shortest graph path
D) Feasibility

### Question 8
Which system-design situation maps to DP thinking?

A) Rendering a button
B) Choosing staged cost/latency trade-offs under constraints
C) Renaming a route
D) Running a shell command

## Section 2: State and Transitions

### Question 9
For Climbing Stairs, what does `dp[i]` mean?

A) Ways to reach step `i`
B) Largest house value
C) Number of graph edges
D) First sorted index

### Question 10
For House Robber, what are the choices at each house?

A) Enqueue or dequeue
B) Move left or right pointer
C) Rotate or sort
D) Skip or take

### Question 11
For Coin Change minimum coins, what should impossible states use?

A) Zero always
B) Infinity-like sentinel
C) The target amount as true
D) A visited set only

### Question 12
For LIS `O(n^2)` DP, what does `dp[i]` represent?

A) LIS anywhere after `i` only
B) Sorted prefix length
C) LIS length ending exactly at `i`
D) Number of islands

### Question 13
For LCS, what does `dp[i][j]` represent?

A) Shortest path from `i` to `j`
B) Sum of grid row and column
C) Last occurrence of target
D) LCS length between prefixes `text1[:i]` and `text2[:j]`

### Question 14
In LCS, when characters match, which state is used?

A) `dp[i + 1][j + 1]`
B) Diagonal `dp[i - 1][j - 1] + 1`
C) Queue front
D) `left + right`

### Question 15
For Word Break, why is `dp[0] = true`?

A) Empty prefix is impossible
B) It stores maximum profit
C) Empty prefix can be segmented with no words
D) It marks a graph node visited

### Question 16
For Unique Paths, each cell depends on:

A) Every future cell
B) Diagonal only
C) Sorted midpoint only
D) Top and left cells

## Section 3: Complexity and Edge Cases

### Question 17
DP time complexity is usually:

A) always `O(log n)`
B) number of states times transition cost
C) always `O(1)`
D) always exponential

### Question 18
What space must top-down DP include?

A) Only the final answer
B) No memory
C) Memo cache and recursion stack
D) Browser storage

### Question 19
When can 1D DP compression corrupt results?

A) When there are no states
B) When input is sorted
C) When using a queue
D) When updates overwrite states still needed later

### Question 20
What is a base case for Coin Change?

A) `dp[0] = infinity`
B) `dp[0] = 0`
C) `dp[amount] = false` always
D) no base case needed

### Question 21
What should Climbing Stairs return for `n = 0` under the standard recurrence?

A) 0 always
B) -1
C) 1 way to do nothing
D) Infinity

### Question 22
Why should LIS return `max(dp)`, not always `dp[n-1]`?

A) The array is sorted
B) The graph is disconnected
C) The last index is always best
D) The best subsequence may end before the last index

### Question 23
What is LCS table size for strings of lengths `m` and `n`?

A) `O(log m)`
B) `O(m * n)`
C) `O(1)` always
D) `O(m + n)` always

### Question 24
What is a safe first step before optimizing DP space?

A) Delete base cases
B) Use greedy instead
C) Write and explain the full recurrence table
D) Remove tests

## Section 4: System Design Transfer

### Question 25
How does DP thinking help in cost/latency planning?

A) It always chooses a graph traversal
B) It removes monitoring needs
C) It renames APIs
D) It models staged choices under constraints

### Question 26
What production risk resembles an incomplete memo key?

A) Better consistency
B) Reusing a cached result for the wrong context
C) Lower latency always
D) No rollback needed

### Question 27
How does impossible-state handling map to system design?

A) Ignore invalid states
B) Retry forever
C) Explicitly represent infeasible plans instead of treating them as zero-cost
D) Hide errors in logs

### Question 28
Which DP concept maps to pipeline optimization?

A) Only recursion depth
B) Only CSS classes
C) Only random search
D) State, transition, objective, and constraints

### Question 29
Why is recurrence explanation more important than code length?

A) It makes code slower
B) It proves correctness and prevents table cargo-culting
C) It avoids edge cases
D) It removes the need for base cases

### Question 30
When should a candidate mention greedy instead of DP?

A) Whenever the prompt has arrays
B) Whenever values are positive
C) When a local-choice proof exists and DP is unnecessary
D) Never

### Question 31
What is the strongest DP wrap-up?

A) "I used an array because this is DP."
B) "I guessed the recurrence."
C) "I skipped impossible cases."
D) "I defined state, objective, transition, base cases, evaluation order, and complexity as states times transition cost."

### Question 32
What should a candidate say when state space is too large?

A) Discuss compression, pruning, sparse memoization, or a different algorithm
B) Ignore it
C) Claim `O(1)` space
D) Increase recursion depth only
