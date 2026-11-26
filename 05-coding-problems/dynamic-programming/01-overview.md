# Dynamic Programming Overview

## Overview

Dynamic programming turns repeated decision trees into a table or memo cache. The table is only useful if each entry has a precise meaning.

Use this checklist before coding:

1. What does one state represent?
2. What answer does that state store?
3. Which smaller states can transition into it?
4. What are the base cases?
5. What order guarantees dependencies are already solved?

## Requirements and constraints

- The recurrence must cover all valid choices.
- The state key must include every variable that affects future decisions.
- Base cases must handle empty input, zero target, first row/column, or impossible values.
- Complexity must be stated as number of states times transition cost.
- Space must include table, memo cache, and recursion stack if used.

## High-level design / approach

| Step | Question | Example |
|---|---|---|
| State | What subproblem is solved? | `dp[i] = best for first i items` |
| Objective | What value is stored? | min coins, max sum, true/false, count |
| Transition | How do choices combine? | take/skip, match/mismatch, move from top/left |
| Base case | What is already known? | amount `0` needs `0` coins |
| Order | What must be solved first? | smaller amount, shorter prefix, previous row |

## Dry run

For Fibonacci-like stairs, `ways[i] = ways[i-1] + ways[i-2]`.

| `i` | Meaning | Value |
|---:|---|---:|
| 0 | one way to stand before climbing | 1 |
| 1 | one single step | 1 |
| 2 | from `1` or `0` | 2 |
| 3 | from `2` or `1` | 3 |
| 4 | from `3` or `2` | 5 |

The recurrence is not magic: the last move is either one step from `i-1` or two steps from `i-2`.

## Language-neutral pseudocode

```text
define state
initialize base cases
for states in dependency-safe order:
    dp[state] = combine(valid previous states)
return answer state
```

Top-down version:

```text
solve(state):
    if state is base case: return base value
    if state in memo: return memo[state]
    memo[state] = combine(solve(next smaller states))
    return memo[state]
```

## Scoring rubric

| Dimension | What interviewers look for |
|---|---|
| State clarity | One sentence defines each DP entry |
| Transition coverage | Includes all valid choices and excludes invalid ones |
| Base cases | Avoids uninitialized or ambiguous table values |
| Order | Computes dependencies before dependents |
| Optimization | Space compression only after table recurrence is correct |

## Common pitfalls

1. Naming `dp` without defining what it stores.
2. Reusing a state that omits a required variable.
3. Compressing space too early and corrupting dependencies.
4. Forgetting impossible sentinels in min/max problems.

## Follow-up questions

1. How do you recover the actual chosen path or items?
2. When is top-down cleaner than bottom-up?
3. When does 1D compression fail?
4. How do you distinguish count, feasibility, and optimization recurrences?

## Variants and extensions

- Rolling arrays for grid/string DP.
- Parent pointers for solution reconstruction.
- Bitset acceleration for subset-style feasibility.
- Memoized recursion for sparse state spaces.

## Cross-links

- [Dynamic Programming Pattern Pack](./README.md)
- [Coin Change](./04-coin-change.md)
- [Longest Common Subsequence](./06-longest-common-subsequence.md)
