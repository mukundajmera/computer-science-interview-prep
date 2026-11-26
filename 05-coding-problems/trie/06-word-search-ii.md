# Word Search II

## Overview

Given a board of characters and a dictionary, return all dictionary words that can be formed by adjacent board cells without reusing a cell in the same word.

The trie prunes DFS paths that are not dictionary prefixes. Without it, searching every word independently repeats too much work.

## Requirements and constraints

- Movement is usually horizontal or vertical; confirm diagonals.
- A cell cannot be reused in the same path.
- Return unique words.
- Board size and dictionary size drive complexity.
- Clarify lowercase alphabet and duplicate words.

## Recognition cue

"Find all words from a dictionary on a board" combines trie prefix pruning with backtracking over the grid.

## Invariant or state definition

During DFS, the current trie node represents the board path string. If the next board character is not a child, no dictionary word can extend that path.

## High-level design / approach

1. Insert all dictionary words into a trie.
2. Store the full word or word id at terminal nodes.
3. Start DFS from each board cell.
4. At each step, move to the child for the current character; stop if missing.
5. When a terminal node is reached, add that word and mark it consumed or use a result set.
6. Mark the board cell visited, explore neighbors, then unmark.

## Dry run

Board:

```text
o a t
h x x
```

Words: `oat`, `oh`, `hat`.

Starting at `o`, path `o-a-t` is possible by moving right twice, so `oat` is found. Starting at `o`, path `o-h` is possible by moving down, so `oh` is found. `hat` fails because after `h-a`, no adjacent `t` is available. If a path reaches prefix `ha` and the trie has no child for the next board character, DFS stops immediately.

## Language-neutral pseudocode

```text
root = build_trie(words)
result = set()

dfs(row, col, node):
    if out_of_bounds or visited:
        return
    char = board[row][col]
    if char not in node.children:
        return
    next_node = node.children[char]
    if next_node.word != null:
        result.add(next_node.word)

    mark visited
    for each neighbor:
        dfs(neighbor.row, neighbor.col, next_node)
    unmark visited

for each cell:
    dfs(cell.row, cell.col, root)
```

## Complexity proof

The worst case can still be exponential in path length because a dense board may produce many valid prefixes. The trie improves practical time by cutting branches as soon as the board path is not a dictionary prefix. Space is dictionary trie size plus recursion depth and result storage.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Trie pruning | Stops board DFS when prefix is absent |
| Backtracking | Marks and unmarks visited cells correctly |
| Deduplication | Prevents duplicate words in output |
| Complexity | Avoids false `O(mnL)` certainty and states branching risk |
| Edge cases | Handles empty board, empty words, and repeated letters |

## Common pitfalls

1. Running a full DFS separately for every word.
2. Forgetting to unmark visited cells.
3. Reusing a board cell in the same word.
4. Returning duplicate words found by different paths.
5. Continuing DFS after trie prefix failure.

## Follow-up questions

1. How would you reduce trie size as words are found?
2. How would diagonal movement change the neighbor loop?
3. How would you parallelize across board regions?
4. How would you enforce a maximum search time in production?

## Variants and extensions

- Boggle solver.
- Board search with wildcards.
- Prefix-pruned route planning.
- Trie-backed content matching on token grids.

## Cross-links

- [Backtracking Pattern Pack](../backtracking/README.md)
- [Wildcard Search](./03-word-dictionary-wildcard-search.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
