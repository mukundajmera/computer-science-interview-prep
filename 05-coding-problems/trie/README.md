# Trie Pattern Pack

A focused coding pattern pack for prefix indexing problems: prefix lookup, wildcard search, dictionary replacement, prefix sums, board search, autocomplete, and lexicographic construction.

## Overview

A trie is a tree-shaped index over characters or tokens. Each edge consumes one symbol, and each node represents a prefix.

Use a trie when the problem repeatedly asks for prefix operations, dictionary membership, prefix-scoped traversal, or incremental search. The interview signal is knowing what each node stores, where words terminate, how traversal fails fast, and how memory grows with total characters rather than number of words alone.

Common variants:

1. Store `children` and `is_word` for exact word and prefix lookup.
2. Add subtree metadata such as `score`, `count`, or `top suggestions`.
3. Support wildcard search with DFS branches.
4. Combine trie traversal with board DFS for word search.
5. Compress paths or cap suggestion lists when memory is the real bottleneck.

## When to Use

Use a trie when the prompt gives you:

1. Many prefix queries over a stable or slowly changing dictionary.
2. Autocomplete, typeahead, command lookup, or route-prefix matching.
3. Wildcard search over dictionary words.
4. A board/grid search that must prune against known word prefixes.
5. Prefix aggregate queries such as "sum values of keys with this prefix."

Strong recognition cues:

- "starts with"
- "autocomplete"
- "search word with '.' wildcard"
- "replace words with shortest root"
- "prefix sum"
- "find all dictionary words on a board"
- "longest word buildable one character at a time"

## When Not to Use

Avoid a trie when:

1. The dataset is tiny and a hash set or sorted list is simpler.
2. You only need exact membership with no prefix behavior.
3. Full-text relevance, typo tolerance, ranking, stemming, or phrase queries dominate. Use a search index instead.
4. Updates are very frequent and subtree metadata would be expensive to maintain.
5. Memory is tighter than latency and a sorted array with binary search is acceptable.

The common warning: a trie optimizes prefix traversal, not semantic search. Autocomplete still needs ranking, freshness, abuse controls, and observability outside the basic data structure.

## Pattern Taxonomy

| Variant | Best fit | Key invariant |
|---|---|---|
| Basic trie | insert/search/startsWith | each path from root represents one prefix |
| Wildcard trie DFS | `.` or one-character wildcard | fixed characters follow one child; wildcard tries all children |
| Shortest-root trie | Replace Words | first terminal node on a path is the shortest replacement |
| Prefix aggregate trie | MapSum | each node stores aggregate value for its prefix |
| Board-search trie | Word Search II | DFS stops when board path is not a dictionary prefix |
| Autocomplete trie | top suggestions per prefix | each prefix node exposes ranked candidates |
| Lexicographic trie | longest buildable word | every prefix on the answer path is terminal |

## Common Failure Modes

1. Forgetting to mark terminal words separately from prefixes.
2. Treating prefix existence as exact word existence.
3. Branching wildcard DFS without bounding word length or recursion depth.
4. Returning duplicate words in Word Search II because the same terminal is found by multiple paths.
5. Not subtracting the old value when updating prefix sums.
6. Keeping unbounded suggestion lists at every autocomplete node.
7. Ignoring memory costs for large alphabets, Unicode, or sparse child maps.
8. Mixing ranking logic with trie traversal until both become hard to test.

## Interview Scoring Focus

| Dimension | Strong signal |
|---|---|
| Node shape | Names children, terminal marker, and any metadata |
| Traversal | Explains exact match, prefix match, and early failure |
| Metadata | Defines how counts, sums, or suggestions update |
| Complexity | Uses word length `L`, total characters, board cells, and branching factor |
| Edge cases | Handles empty string, duplicate insert, prefixes that are also words, and no-match paths |
| Transfer | Separates prefix lookup from ranking, relevance, storage, and freshness |

## 60-90 Second Answer

Say:

"I use a trie when the core operation is prefix-constrained. Each node represents the prefix formed by the path from the root. For exact search I walk characters and require the last node to be terminal; for `startsWith` I only require the path to exist. For wildcard search, fixed characters choose one child while wildcards branch over children. For autocomplete, the trie gets me to the prefix node quickly, but ranking needs separate metadata such as top suggestions per node or a downstream ranker. The complexity is usually `O(L)` per insert/search for word length `L`, with memory proportional to total stored characters, so I will call out compression or capped metadata if scale matters."

## Problem Track

1. [01-overview.md](./01-overview.md)
2. [02-implement-trie-prefix-tree.md](./02-implement-trie-prefix-tree.md)
3. [03-word-dictionary-wildcard-search.md](./03-word-dictionary-wildcard-search.md)
4. [04-replace-words.md](./04-replace-words.md)
5. [05-map-sum-pairs.md](./05-map-sum-pairs.md)
6. [06-word-search-ii.md](./06-word-search-ii.md)
7. [07-design-search-autocomplete-system.md](./07-design-search-autocomplete-system.md)
8. [08-longest-word-in-dictionary.md](./08-longest-word-in-dictionary.md)

## Cross-links

- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [Complexity Reference](../../00-theory/cheat-sheets/complexity-reference.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
- [Elasticsearch](../../03-hld-concepts/elasticsearch/THEORY.md)
- [Social Post Search](../../04-hld-projects/social-post-search/)
- [Trie Quiz](../../quizzes/trie-quiz.md)
- [Trie Flashcards](../../flashcards/trie.md)
- [Coach Answer: Coding Trie](../../solutions/coding-trie.md)
