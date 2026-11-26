# Longest Word in Dictionary

## Overview

Given a list of words, find the longest word that can be built one character at a time by other words in the list. If there is a tie, return the lexicographically smallest word.

A trie helps because a valid answer path must have every prefix marked as a complete word.

## Requirements and constraints

- Every prefix of the answer, excluding the empty prefix, must be present as a word.
- Return the longest valid word.
- Break ties lexicographically.
- Clarify lowercase alphabet.
- Duplicate words should not affect the answer.

## Recognition cue

"Build one character at a time" means every prefix must be terminal. This is a trie terminal-marker problem, not just a prefix existence problem.

## Invariant or state definition

DFS should only enter child nodes that are terminal words. Therefore every path explored is buildable from shorter valid words.

## High-level design / approach

1. Insert all words into a trie.
2. DFS from the root.
3. Visit children in lexicographic order.
4. Only traverse a child if `child.is_word` is true.
5. Update the answer when the current word is longer.
6. Lexicographic traversal handles ties if you only replace on strictly longer words.

## Dry run

Words: `w`, `wo`, `wor`, `worl`, `world`, `banana`.

| Candidate | Prefixes present? | Valid? |
|---|---|---:|
| `world` | `w`, `wo`, `wor`, `worl` | true |
| `banana` | `b`, `ba`, ... missing | false |

Answer: `world`.

## Language-neutral pseudocode

```text
build trie from words
answer = ""

dfs(node, current):
    if len(current) > len(answer):
        answer = current
    for char in sorted(node.children.keys):
        child = node.children[char]
        if child.is_word:
            dfs(child, current + char)

dfs(root, "")
return answer
```

## Complexity proof

Building the trie costs `O(total_chars)`. DFS visits only terminal-prefix nodes. Sorting child keys costs up to alphabet-size work per visited node; with fixed lowercase letters, this is constant. Space is trie size plus recursion depth.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Prefix condition | Requires every intermediate prefix to be terminal |
| Tie-breaking | Handles lexicographically smallest valid word |
| Traversal | Visits only buildable nodes |
| Complexity | Uses total characters and alphabet assumptions |
| Edge cases | Handles no valid multi-character word and duplicate inputs |

## Common pitfalls

1. Accepting a word when its path exists but prefixes are not terminal.
2. Sorting all words and doing repeated substring checks without discussing cost.
3. Breaking lexicographic ties incorrectly.
4. Starting DFS from non-terminal children.
5. Treating the empty prefix as a stored word requirement.

## Follow-up questions

1. How would a hash set solution compare?
2. How would you return all longest buildable words?
3. How would you support streaming inserts?
4. How would uppercase or Unicode affect ordering?

## Variants and extensions

- Longest buildable command.
- Prefix-valid route set.
- Dictionary quality checks.
- Lexicographic trie traversal.

## Cross-links

- [Trie Overview](./01-overview.md)
- [Implement Trie](./02-implement-trie-prefix-tree.md)
- [Complexity Reference](../../00-theory/cheat-sheets/complexity-reference.md)
