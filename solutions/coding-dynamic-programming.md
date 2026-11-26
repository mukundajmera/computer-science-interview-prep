# Coach Answer: Coding Dynamic Programming Pack

> Type: Coding Pattern Drill
> Difficulty: Intermediate
> Time Target: 50 minutes

## Phase 1 - Problem Framing

Strong candidates do not say "this is DP" and start filling an array. They define the model.

1. Identify the objective: maximize, minimize, count, or decide feasibility.
2. Define the state in one sentence.
3. Confirm the state contains all variables that affect future decisions.
4. Write base cases.
5. Write the transition from smaller states.
6. Choose top-down memoization or bottom-up tabulation.
7. State complexity as states times transition cost.

## Phase 2 - Canonical Templates

### Template A: 1D Bottom-Up DP

```text
dp = base-initialized array
for i in dependency order:
    dp[i] = combine(previous states)
return target state
```

Use for Climbing Stairs, House Robber, and many prefix decisions.

### Template B: Min/Max With Impossible States

```text
dp = array filled with infinity or negative infinity
dp[base] = neutral value
for state in states:
    for choice in choices:
        if previous state is possible:
            dp[state] = best(dp[state], dp[previous] + cost_or_value)
```

Use for Coin Change and budget-style optimization.

### Template C: 2D Prefix DP

```text
dp = matrix with one extra row and column
for i from 1..m:
    for j from 1..n:
        if current items match:
            dp[i][j] = diagonal transition
        else:
            dp[i][j] = best(skip one side)
```

Use for LCS and related string alignment problems.

### Template D: Boolean Prefix DP

```text
dp[0] = true
for end in 1..n:
    for split in 0..end-1:
        if dp[split] and suffix(split, end) is valid:
            dp[end] = true
            break
```

Use for Word Break and segmentation feasibility.

## Phase 3 - Problem-by-Problem Walkthrough

1. **Climbing Stairs**
   - State: ways to reach step `i`.
   - Last move: one or two steps.

2. **House Robber**
   - State: best value through index `i`.
   - Choice: skip current or take current plus `i - 2`.

3. **Coin Change**
   - State: min coins for amount `a`.
   - Sentinel: infinity for impossible.
   - Greedy is not generally safe.

4. **Longest Increasing Subsequence**
   - State: LIS ending exactly at `i`.
   - Return `max(dp)`, not only the last state.

5. **Longest Common Subsequence**
   - State: LCS of two prefixes.
   - Match uses diagonal; mismatch skips one side.

6. **Word Break**
   - State: whether prefix `s[:i]` is segmentable.
   - Base: empty prefix is true.

7. **Unique Paths**
   - State: paths to cell `(r, c)`.
   - Transition: top plus left.

## Phase 4 - Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| State definition | 25% | One precise sentence for each table entry |
| Transition proof | 25% | Covers every valid choice and no invalid choices |
| Base cases | 15% | Handles empty, zero, first row/column, and impossible states |
| Evaluation order | 15% | Dependencies are solved before use |
| Complexity | 10% | Counts states, transition cost, table, memo, and stack |
| Communication | 10% | Explains why DP beats brute force and when greedy would be better |

## Phase 5 - Common Pitfalls

1. Writing recurrence before state.
2. Missing a state dimension.
3. Using ambiguous sentinel values.
4. Confusing subsequence with substring or subarray.
5. Compressing DP in the wrong direction.
6. Returning the wrong terminal state.
7. Ignoring substring creation cost.
8. Claiming recursion stack is free.

## System Design Transfer Script

Use this table to translate DP discipline into production design trade-offs.

| DP concept | Production analogue | Scale risk | Validation signal |
|---|---|---|---|
| Objective, state, transition | Cost/latency optimizer for routing, batching, or placement | State-space explosion, stale cost model, overfitting to yesterday's traffic | p95 latency, cost per request, optimality gap, cache hit rate |
| Memoization key | Cache key and invalidation policy | Wrong-context reuse, stale answers, privacy leakage across tenants | Cache correctness tests, invalidation lag, tenant-key coverage |
| Impossible-state sentinel | Explicit rejection state in planning or scheduling | Silent fallback to invalid routes or impossible allocations | Rejection reason distribution, planner failure rate, audit logs |
| Space compression | Rolling-window state in stream processing or scoring | Dropping a dependency needed for correctness | Replay parity, memory profile, bounded-state invariant checks |

## Follow-Up Drill Set

1. Min Cost Climbing Stairs.
2. House Robber II.
3. Coin Change II.
4. Longest Palindromic Subsequence.
5. Edit Distance.
6. Decode Ways.
7. Unique Paths II.
8. 0/1 Knapsack.

## Cross-links

- [Dynamic Programming Pattern Pack](../05-coding-problems/dynamic-programming/README.md)
- [Dynamic Programming Quiz](../quizzes/dynamic-programming-quiz.md)
- [Dynamic Programming Flashcards](../flashcards/dynamic-programming.md)
- [Job Scheduler HLD](../04-hld-projects/job-scheduler/)
- [Token / Cost / Latency Planning](../06-genai-systems/00-concepts/token-cost-latency/README.md)
