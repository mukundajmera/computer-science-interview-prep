# Backtracking Overview

## Overview

Backtracking is the pattern for exploring a decision tree while keeping only valid partial states alive.

The algorithm is recursive, but recursion alone is not the pattern. The pattern is the contract:

- define the state;
- choose among legal next candidates;
- reject invalid partial states;
- recurse;
- restore state before trying the next candidate.

## Mental model

Think of every recursive call as owning one prefix of the answer. That prefix may be a list, a string partition, a board, or a grid path.

The call has one job: extend that prefix with every legal next choice. If a choice makes the prefix invalid, skip it immediately. If a complete valid answer is reached, copy the answer into the result.

## Requirements and constraints

- State whether the prompt asks for all answers, one answer, a count, or an optimized answer.
- Define the base case before writing the loop.
- Track mutable state explicitly: path, used set, visited cells, board, row/column/diagonal sets, or remaining target.
- Copy mutable answers before appending them to results.
- Report exponential complexity honestly.

## High-level design / approach

1. Choose a state representation: index, path, remaining target, board position, or grid coordinate.
2. Define the invariant for a valid partial state.
3. Generate candidate choices for the current state.
4. Prune candidates that violate the invariant.
5. Apply the candidate.
6. Recurse.
7. Undo the candidate.
8. Emit a copied answer at the base case.

## Dry run

For subsets of `[1, 2]`, state is `(index, path)`.

```text
start: index 0, path []
skip 1 -> index 1, path []
  skip 2 -> emit []
  take 2 -> emit [2]
take 1 -> index 1, path [1]
  skip 2 -> emit [1]
  take 2 -> emit [1, 2]
```

The invariant is that `path` contains choices made only from indexes before the current index.

## Language-neutral pseudocode

```text
backtrack(state):
    if state is complete:
        results.add(copy(current_answer))
        return

    for choice in legal_choices(state):
        if choice violates constraints:
            continue
        apply choice
        backtrack(next_state)
        undo choice
```

## Complexity

- Subsets: `O(n * 2^n)` time to materialize all subsets, `O(n)` recursion space beyond output.
- Permutations: `O(n * n!)` time to materialize all permutations, `O(n)` recursion space beyond output.
- Constraint boards: exponential in empty cells or rows, reduced by pruning.
- Grid path search: often `O(rows * cols * branching^word_length)` with visited-path space.

Output size usually dominates. Say whether complexity includes copying each emitted answer.

## Backtracking checklist

Before coding, answer:

1. What is the recursive state?
2. What is the complete base case?
3. What choices are legal from this state?
4. What invariant makes a partial answer valid?
5. What state must be undone after recursion?
6. How are duplicates prevented?

## Backtracking vs BFS, DP, and Greedy

| Prompt shape | Likely pattern | Why |
|---|---|---|
| "all valid boards" | backtracking | must enumerate constrained assignments |
| "shortest path in unweighted graph" | BFS | first discovery by layer is shortest |
| "count ways with overlapping suffixes" | DP | repeated subproblems should be reused |
| "maximum non-overlapping intervals" | greedy | earliest-finish choice has a proof |

## System-design transfer

Backtracking thinking appears in production planning systems when a scheduler, planner, or rules engine tries assignments and rolls them back:

- workflow planners try dependency-compatible schedules;
- policy engines test rule combinations;
- resource allocators try placement candidates with constraints;
- migration planners simulate dependency-safe orders.

Production systems usually need timeouts, bounded search, audit logs, and fallback plans because complete search can be too expensive.

## Interview-ready wrap-up

"My recursion maintains a valid partial answer. Every branch applies one legal choice, explores all consequences, and restores the state. When the state is complete, I copy the answer. The pruning rule is safe because it only rejects prefixes that already violate the problem constraints."

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Recognition | Identifies enumeration or constraint satisfaction |
| State | Names all changing fields in the recursion frame |
| Invariant | States why the partial answer is valid |
| Pruning | Rejects invalid choices without losing valid answers |
| Restore | Shows exact undo operation |
| Complexity | Gives exponential or output-sensitive bound |

## Common pitfalls

1. Appending the same mutable list reference to every result.
2. Forgetting to unmark a used item or board cell.
3. Missing duplicate-skip logic for repeated candidates.
4. Calling recursion after the state is already invalid.
5. Using global state without resetting it between calls.

## Follow-up questions

1. How would you return only the count?
2. Where would memoization help?
3. How would you handle duplicate input values?
4. How would you enforce a time limit in production?

## Variants and extensions

- Backtracking with memoization for repeated suffix states.
- Branch-and-bound for optimization variants.
- Bitmask state for compact constraint checks.
- Iterative stack simulation when recursion depth is a concern.

## Cross-links

- [Backtracking Pattern Pack](./README.md)
- [Subsets](./02-subsets.md)
- [Permutations](./03-permutations.md)
- [Combination Sum](./04-combination-sum.md)
