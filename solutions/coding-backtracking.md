# Coach Answer: Coding Backtracking Pack

> Type: Coding Pattern Drill
> Difficulty: Intermediate
> Time Target: 45 minutes

## Phase 1 - Problem Framing

Strong candidates do not start by saying "I will recurse." They define the decision tree and the valid partial state.

1. Identify whether the prompt asks for all answers, one answer, a count, or an optimized answer.
2. Define the recursive state: index, path, remaining target, board row, grid coordinate, or empty-cell position.
3. Define the invariant that makes a partial state valid.
4. Define candidate choices from the current state.
5. Define the pruning rule.
6. Define the base case and whether the answer must be copied.
7. Name every mutated field that must be undone after recursion.

## Phase 2 - Canonical Templates

### Template A: Include / Exclude

```text
dfs(index):
    if index == n:
        emit copy(path)
        return

    dfs(index + 1)

    path.add(items[index])
    dfs(index + 1)
    path.remove_last()
```

Use for subsets and binary choose-or-skip decisions.

### Template B: Used-Set Permutations

```text
dfs():
    if path.length == n:
        emit copy(path)
        return

    for i in 0..n-1:
        if used[i]:
            continue
        used[i] = true
        path.add(items[i])
        dfs()
        path.remove_last()
        used[i] = false
```

Use when every output must use each item exactly once.

Duplicate-aware permutation variant:

```text
sort items
dfs():
    if path.length == n:
        emit copy(path)
        return

    for i in 0..n-1:
        if used[i]:
            continue
        if i > 0 and items[i] == items[i - 1] and not used[i - 1]:
            continue
        used[i] = true
        path.add(items[i])
        dfs()
        path.remove_last()
        used[i] = false
```

The skip rule means "do not start a new same-depth branch with the second copy before the first copy has been used in this permutation prefix."

### Template C: Start-Index Combinations

```text
dfs(start, remaining):
    if remaining == 0:
        emit copy(path)
        return

    for i from start to n-1:
        if candidates[i] > remaining:
            break
        path.add(candidates[i])
        dfs(i, remaining - candidates[i])      // reuse allowed
        path.remove_last()
```

Use `i + 1` instead of `i` when each candidate can be used only once.

Duplicate-aware combination variant:

```text
sort candidates
dfs(start, remaining):
    if remaining == 0:
        emit copy(path)
        return

    for i from start to n-1:
        if i > start and candidates[i] == candidates[i - 1]:
            continue
        if candidates[i] > remaining:
            break
        path.add(candidates[i])
        dfs(i + 1, remaining - candidates[i])
        path.remove_last()
```

Use the same same-depth skip for Subsets II when input values can repeat. For high-duplication permutation inputs, a frequency map is another safe template: choose a value only while its remaining count is positive, decrement before recursion, and increment during rollback.

### Template D: Grid Path Backtracking

```text
dfs(r, c, index):
    if index == target.length:
        return true
    if out_of_bounds or visited[r][c] or grid[r][c] != target[index]:
        return false

    visited[r][c] = true
    for next cell in four directions:
        if dfs(next.r, next.c, index + 1):
            visited[r][c] = false
            return true
    visited[r][c] = false
    return false
```

Use when a cell may be used once per active path but may be reused by different paths.

### Template E: Constraint Sets

```text
dfs(row):
    if row == n:
        emit copy_board(board)
        return

    for col in 0..n-1:
        if col in cols or row - col in diag1 or row + col in diag2:
            continue
        place choice and add constraints
        dfs(row + 1)
        remove constraints and undo choice
```

Use for N-Queens, Sudoku-style placement, and resource assignment with conflict rules.

Copy the board or serialize rows before emitting. Otherwise every result can point at the same mutable board that later recursion steps keep changing.

## Phase 3 - Problem-by-Problem Walkthrough

1. **Subsets**
   - State: `index` and `path`.
   - Choice: include or exclude current item.
   - Base case: index reaches length.

2. **Permutations**
   - State: `path` plus `used` indexes.
   - Choice: any unused item.
   - Base case: path length reaches `n`.

3. **Combination Sum**
   - State: `start`, `remaining`, and `path`.
   - Choice: candidates from `start` onward.
   - Reuse: recurse with `i`; single-use variant recurses with `i + 1`.

4. **Word Search**
   - State: grid cell and word index.
   - Invariant: active path spells the prefix and contains no repeated cell.
   - Restore visited state on every return path.

5. **Palindrome Partitioning**
   - State: start index and list of palindrome segments.
   - Choice: every palindrome prefix from the current start.
   - Optional optimization: precompute palindrome ranges.

6. **N-Queens**
   - State: current row, board, columns, and diagonals.
   - Prune with `col`, `row - col`, and `row + col`.

7. **Sudoku Solver**
   - State: empty-cell position plus row, column, and box sets.
   - Stop after one solution unless all solutions are requested.
   - Restore both board cell and constraint sets after failed candidates.

## Phase 4 - Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| State definition | 20% | Names all fields needed in a recursion frame |
| Base case | 15% | Emits or stops at the exact completion condition |
| Validity and pruning | 20% | Rejects invalid partial states without losing valid answers |
| Restore discipline | 20% | Undoes every mutation before sibling branches |
| Duplicate handling | 10% | Handles repeated inputs or explains distinct-input assumption |
| Complexity | 10% | Gives output-sensitive exponential bounds and stack space |
| Communication | 5% | Differentiates backtracking from BFS, DP, and greedy |

## Phase 5 - Common Pitfalls

1. Storing mutable `path` or `board` by reference.
2. Forgetting an undo step for a set, board cell, or visited marker.
3. Using one global visited set for all Word Search starts.
4. Emitting duplicate combinations because order was not constrained.
5. Missing diagonal checks in N-Queens.
6. Treating Sudoku as solved after filling a locally valid digit.
7. Calling exponential enumeration "linear" because the loop looks small.
8. Using backtracking for a shortest-path prompt that should use BFS.

## System Design Transfer Script

| Backtracking concept | Production analogue | Scale risk | Validation signal |
|---|---|---|---|
| Valid partial state | candidate deployment, schedule, or placement plan | hidden invalid plan state | rejected-plan reason counts, invariant checks |
| Pruning rule | policy or capacity precheck | over-pruning valid options or under-pruning invalid ones | false reject rate, conflict escape rate |
| Undo step | transaction rollback or candidate-state isolation | state leakage across attempts | rollback failures, dirty-state audits |
| Constraint sets | fast conflict indexes | stale constraints allow invalid placement | conflict index freshness, reconciliation errors |
| Bounded search | planner with timeout and fallback | search explosion | timeout rate, branch count, fallback usage |

## Follow-Up Drill Set

1. Subsets II.
2. Permutations II.
3. Combination Sum II.
4. Word Search II.
5. Restore IP Addresses.
6. Generate Parentheses.
7. Letter Combinations of a Phone Number.
8. N-Queens II.

## Cross-links

- [Backtracking Pattern Pack](../05-coding-problems/backtracking/README.md)
- [Backtracking Quiz](../quizzes/backtracking-quiz.md)
- [Backtracking Flashcards](../flashcards/backtracking.md)
