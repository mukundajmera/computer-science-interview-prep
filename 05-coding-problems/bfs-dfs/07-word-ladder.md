# Word Ladder

## Overview

Given `beginWord`, `endWord`, and a dictionary, return the length of the shortest transformation sequence where each step changes one letter and every intermediate word is in the dictionary.

This is shortest path in an unweighted implicit graph: each word is a node, and an edge exists between words that differ by one character.

## Requirements and constraints

- Return `0` when no sequence exists.
- Each step changes exactly one character.
- All intermediate words must be in the word list.
- BFS gives shortest sequence length.

## Recognition cue

"Shortest transformation", "one step changes state", and "unweighted" signal BFS over an implicit state graph.

## Invariant

When a word is first dequeued or discovered by BFS, the associated distance is the shortest number of transformations needed to reach it.

## High-level design / approach

1. Put dictionary words in a set for `O(1)` membership checks.
2. If `endWord` is absent, return `0`.
3. Start BFS from `beginWord` with distance `1`.
4. For each position in the current word, try replacing it with every letter.
5. If the candidate is in the dictionary and unvisited, mark visited and enqueue with `distance + 1`.
6. Return distance when `endWord` is found.

## Dry run

`hit -> cog`, dictionary: `hot, dot, dog, lot, log, cog`.

| Distance | Frontier | Next valid words |
|---:|---|---|
| 1 | `hit` | `hot` |
| 2 | `hot` | `dot`, `lot` |
| 3 | `dot`, `lot` | `dog`, `log` |
| 4 | `dog`, `log` | `cog` |
| 5 | `cog` | found |

Answer: `5`.

## Language-neutral pseudocode

```text
words = set(wordList)
if endWord not in words: return 0
queue = [(beginWord, 1)]
visited = {beginWord}
while queue:
    word, distance = queue.pop_front()
    if word == endWord: return distance
    for each index i:
        for each letter a..z:
            candidate = replace word[i] with letter
            if candidate in words and candidate not visited:
                visited.add(candidate)
                queue.push_back(candidate, distance + 1)
return 0
```

## Complexity proof

Let `N` be the number of dictionary words and `L` be the word length. A straightforward neighbor generator visits each discovered word once, tries `L` positions, and tries `26` replacement letters per position. Each candidate construction or hash lookup can cost up to `O(L)` in languages that allocate a new string. That gives `O(N * L * 26 * L)`, usually written as `O(N * L^2)` because the alphabet is constant.

Auxiliary space is `O(N * L)` for the dictionary/visited words plus the BFS queue. If you precompute wildcard buckets such as `h*t`, preprocessing and storage are also `O(N * L^2)` when materialized as strings.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Implicit graph | Does not build all pairwise edges naively unless justified |
| BFS choice | Explains shortest unweighted path |
| Visited timing | Marks before enqueue to avoid repeated states |
| Complexity | Accounts for word length, alphabet size, and dictionary size |

## Common pitfalls

1. Using DFS and returning a non-shortest path.
2. Forgetting that `endWord` must be in the dictionary.
3. Re-enqueueing the same word from multiple parents.
4. Counting edges when the prompt asks for sequence length.

## Follow-up questions

1. How would bidirectional BFS improve this?
2. How would wildcard buckets reduce neighbor generation?
3. How would you return the actual path, not just length?
4. How would you bound memory if the dictionary is too large to keep in one process?

## Variants and extensions

- Bidirectional BFS.
- Shortest path in a lock/combo state space.
- Autocomplete typo correction candidate graph.

## Cross-links

- [BFS / DFS Overview](./01-overview.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
