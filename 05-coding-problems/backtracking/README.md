# Backtracking Pattern Pack

A focused coding pattern pack for exhaustive search problems where each step makes a choice, validates constraints, recurses, and then undoes the choice.

## Overview

Backtracking is controlled brute force.

It is the right pattern when the answer depends on exploring a decision tree but invalid branches can be pruned early. The interview signal is not merely recursion; it is the discipline of defining the state, the choices from that state, the validity rule, the base case, and the choose/explore/unchoose step.

The core loop is:

1. choose a candidate;
2. check whether it keeps the partial state valid;
3. recurse;
4. unchoose the candidate before trying the next option.

## When to Use

Use backtracking when the problem gives you:

1. A prompt asking for all valid combinations, subsets, permutations, partitions, boards, or assignments.
2. A constraint satisfaction problem such as N-Queens or Sudoku.
3. A search space where partial states can be rejected before completion.
4. A path search where each cell, character, or item can be used under strict rules.
5. A need to preserve every valid answer, not just count or optimize one answer.

Strong recognition cues:

- "generate all"
- "all possible"
- "choose any subset"
- "permutation"
- "partition into valid pieces"
- "place items so no conflicts exist"
- "can this word/path/board be formed"

## When Not to Use

Avoid backtracking when:

1. The prompt asks for one shortest path in an unweighted graph; use BFS.
2. The problem has overlapping subproblems and asks for counts or optimal values; use DP or memoization.
3. A greedy proof gives a safe local choice.
4. The search space is huge and no pruning rule exists.
5. The input is production-scale and the task needs bounded latency rather than complete enumeration.

Backtracking can be combined with memoization, but plain backtracking alone is usually too slow for repeated subproblems.

## Pattern Taxonomy

| Variant | Best fit | Key invariant |
|---|---|---|
| Include/exclude recursion | subsets | each index is either chosen or skipped exactly once |
| Swap-based generation | permutations | prefix positions are fixed and suffix positions remain available |
| Start-index combinations | combination sum | candidates before `start` cannot be reused in the current order |
| Grid path search | word search | path cells are used at most once in the active recursion path |
| Partition recursion | palindrome partitioning | every emitted prefix segment satisfies the predicate |
| Constraint placement | N-Queens | rows processed so far have non-conflicting queens |
| Constraint propagation | Sudoku | every filled digit respects row, column, and box constraints |
| Branch-and-bound search | optimized variants | prune when current partial state cannot beat the best answer |

## Common Failure Modes

1. Forgetting to undo state after recursion.
2. Sharing a mutable path object into results without copying it.
3. Generating duplicate answers from duplicate candidates.
4. Missing the base case or emitting at the wrong recursion depth.
5. Pruning with a rule that rejects valid future answers.
6. Treating recursion stack space as `O(1)`.
7. Mutating an input board without restoring it.
8. Using backtracking where DP, BFS, or greedy is the actual intended pattern.

## Interview Scoring Focus

| Dimension | Strong signal |
|---|---|
| State definition | Names index, path, remaining target, board, or constraint sets |
| Choice order | Explains which candidates are legal from the current state |
| Validity rule | Prunes invalid partial states before deeper recursion |
| Undo discipline | Restores path, board, and constraint sets after each branch |
| Duplicate handling | Sorts or skips equal candidates when needed |
| Complexity honesty | States output-sensitive or exponential bounds and recursion space |

## 60-90 Second Answer

Say:

"I use backtracking when I need to explore a decision tree of valid partial states. I define the recursive state, such as index plus current path, remaining target, or board position. At each frame I try legal choices, prune choices that violate constraints, recurse, and then undo the choice so sibling branches start from the same state. The invariant is that the partial answer is always valid before recursion. When the base case is reached, I copy the current path or board into the result. Complexity is usually exponential or output-sensitive, with recursion depth and mutable state called out explicitly."

## Problem Track

1. [01-overview.md](./01-overview.md)
2. [02-subsets.md](./02-subsets.md)
3. [03-permutations.md](./03-permutations.md)
4. [04-combination-sum.md](./04-combination-sum.md)
5. [05-word-search.md](./05-word-search.md)
6. [06-palindrome-partitioning.md](./06-palindrome-partitioning.md)
7. [07-n-queens.md](./07-n-queens.md)
8. [08-sudoku-solver.md](./08-sudoku-solver.md)

## Cross-links

- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
- [Workflow Orchestration](../../03-hld-concepts/workflow-orchestration/THEORY.md)
- [Backtracking Quiz](../../quizzes/backtracking-quiz.md)
- [Backtracking Flashcards](../../flashcards/backtracking.md)
- [Coach Answer: Coding Backtracking](../../solutions/coding-backtracking.md)
