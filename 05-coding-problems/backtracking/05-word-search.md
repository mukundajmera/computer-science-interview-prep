# Word Search

## Overview

Given a grid of characters and a word, determine whether the word can be formed by moving horizontally or vertically through adjacent cells without reusing a cell in the same path.

This is backtracking over grid paths.

## Requirements and constraints

- Match the word in order.
- Move in four directions unless the prompt allows diagonals.
- Do not reuse a cell within the active path.
- Restore the board or visited state after exploring each branch.

## Recognition cue

"Can this word be formed from adjacent cells without reusing cells" signals DFS backtracking with a path-local visited set.

## Invariant or state definition

At state `(row, col, index)`, cells in the active path spell `word[0:index]`, and each active path cell is used once.

## High-level design / approach

1. For every cell matching the first character, start DFS.
2. In DFS, return true if `index == word.length`.
3. Reject out-of-bounds cells, character mismatches, and already-used cells.
4. Mark the cell as visited.
5. Try four neighbors for the next character.
6. Unmark the cell before returning.

## Dry run

Grid:

```text
A B C
S F C
A D E
```

Word: `ABCCED`.

| Step | Cell | Matched prefix |
|---|---|---|
| 1 | `(0,0)` A | `A` |
| 2 | `(0,1)` B | `AB` |
| 3 | `(0,2)` C | `ABC` |
| 4 | `(1,2)` C | `ABCC` |
| 5 | `(2,2)` E | `ABCCE` |
| 6 | `(2,1)` D | `ABCCED` |

The path succeeds without reusing a cell.

## Language-neutral pseudocode

```text
for each cell r, c:
    if dfs(r, c, 0):
        return true
return false

dfs(r, c, index):
    if index == word.length:
        return true
    if out of bounds or visited[r][c] or board[r][c] != word[index]:
        return false

    visited[r][c] = true
    for each direction:
        if dfs(next_r, next_c, index + 1):
            visited[r][c] = false
            return true
    visited[r][c] = false
    return false
```

## Complexity

- Time: `O(rows * cols * 4 * 3^(L - 1))` in a common bound, where `L` is word length. After the first move, the path usually avoids immediately going back to the previous cell.
- Space: `O(L)` recursion depth plus visited state if separate.
- If mutating the board in place for visited markers, auxiliary visited storage can be avoided, but the board must be restored.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Start points | Tries every cell as a possible word start |
| Visited path | Prevents reuse only within the active path |
| Restore | Unmarks cells on success and failure paths |
| Complexity | Uses word length, grid size, and branching factor |

## Common pitfalls

1. Using a global visited set across different starting cells.
2. Forgetting to restore visited state before returning true.
3. Allowing diagonal movement accidentally.
4. Checking `index == length` after accessing `word[index]`.

## Follow-up questions

1. How would you search for many words in the same board?
2. How would a trie reduce repeated prefix work?
3. How would you avoid mutating the board?

## Variants and extensions

- Word Search II using a trie.
- Boggle-style dictionary lookup.
- Grid path with obstacles.
- Prefix pruning with frequency counts.

## Cross-links

- [Backtracking Overview](./01-overview.md)
- [N-Queens](./07-n-queens.md)
- [Sudoku Solver](./08-sudoku-solver.md)
