# Dynamic Programming Pattern Pack

A focused coding pattern pack for problems where the answer can be built from smaller overlapping subproblems: 1D recurrence, grid DP, sequence DP, knapsack-style choice DP, memoized recursion, and bottom-up tabulation.

## Overview

Dynamic programming is not "use an array." It is a modeling discipline:

1. Define the state.
2. Define the objective for that state.
3. Write the transition from smaller states.
4. Set base cases.
5. Choose memoized recursion or bottom-up order.

The strongest interview answers make the recurrence feel inevitable. If you cannot say what `dp[i]` or `dp[i][j]` means in one sentence, the code will usually become guesswork.

## When to Use

Use dynamic programming when all of these are true:

1. The problem asks for an optimum, count, feasibility result, or best value.
2. A decision can be expressed using smaller subproblems.
3. Subproblems overlap enough that recomputation is expensive.
4. The state can be bounded by input size.
5. Local greedy choices are not obviously safe.

Strong recognition cues:

- "maximum/minimum ways", "number of ways", "can form", "fewest coins"
- "subsequence", "prefixes of two strings", "choose or skip"
- "grid paths", "from top-left to bottom-right"
- "not adjacent", "capacity", "target sum"
- "exponential recursion with repeated calls"

## When Not to Use

Avoid DP when:

1. There is no overlapping subproblem.
2. A simple greedy proof is valid and much simpler.
3. The state space is too large without compression or pruning.
4. The problem asks to enumerate all outputs, not count or optimize them.
5. You cannot define a complete state key.

## Pattern Taxonomy

| Variant | Best fit | State example |
|---|---|---|
| 1D DP | linear choices, previous few states | `dp[i] = best answer for prefix ending at i` |
| Grid DP | paths or costs on rows/columns | `dp[r][c] = answer to reach cell r,c` |
| Sequence DP | subsequence/string alignment | `dp[i][j] = answer for prefixes a[:i], b[:j]` |
| Choice DP | choose/skip, capacity, target | `dp[i][amount]` or compressed `dp[amount]` |
| Memoized DFS | natural recursion with repeated states | `memo[state] = solved result for that state` |
| State compression | table depends on limited prior rows/items | one row, two variables, or rolling arrays |

## Common Failure Modes

1. Writing code before defining the state.
2. Missing base cases.
3. Memoizing with an incomplete key.
4. Updating compressed DP in the wrong direction.
5. Confusing substring, subarray, and subsequence.
6. Treating greedy as DP or DP as greedy without proof.
7. Using `0` as an impossible-state sentinel when `0` is a valid answer.
8. Claiming `O(1)` space while using a memo cache or recursion stack.

## Interview Scoring Focus

| Dimension | Strong signal |
|---|---|
| State definition | Says exactly what each DP cell means |
| Transition proof | Explains why all valid previous choices are covered |
| Base cases | Handles empty prefix, amount zero, first row/column, or impossible states |
| Evaluation order | Uses memoized recursion or bottom-up order that respects dependencies |
| Complexity honesty | Counts table size, transition cost, memo cache, and recursion stack |
| Follow-up depth | Can optimize space, recover path, or switch between feasibility/count/optimization |

## 60-90 Second Answer

Say:

"I use DP when a brute-force recursion repeats the same subproblems. I first define a state, such as `dp[i]` for a prefix, `dp[r][c]` for a grid cell, or `dp[i][j]` for two string prefixes. Then I define the objective: maximum value, minimum cost, count, or feasibility. The transition considers the choices that can lead into that state, and base cases handle empty prefixes or zero targets. I choose top-down memoization if the recursion is more natural, and bottom-up tabulation if ordering is simple. Complexity is the number of states times the transition cost, with space equal to the table or compressed state."

## Problem Track

1. [01-overview.md](./01-overview.md)
2. [02-climbing-stairs.md](./02-climbing-stairs.md)
3. [03-house-robber.md](./03-house-robber.md)
4. [04-coin-change.md](./04-coin-change.md)
5. [05-longest-increasing-subsequence.md](./05-longest-increasing-subsequence.md)
6. [06-longest-common-subsequence.md](./06-longest-common-subsequence.md)
7. [07-word-break.md](./07-word-break.md)
8. [08-unique-paths.md](./08-unique-paths.md)

## Cross-links

- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
- [Job Scheduler HLD](../../04-hld-projects/job-scheduler/)
- [Token / Cost / Latency Planning](../../06-genai-systems/00-concepts/token-cost-latency/README.md)
- [Dynamic Programming Quiz](../../quizzes/dynamic-programming-quiz.md)
- [Dynamic Programming Flashcards](../../flashcards/dynamic-programming.md)
- [Coach Answer: Coding Dynamic Programming](../../solutions/coding-dynamic-programming.md)
