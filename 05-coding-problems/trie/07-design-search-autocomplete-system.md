# Design Search Autocomplete System

## Overview

Design an autocomplete data structure that records sentences or terms and returns the top suggestions for a prefix.

A trie locates the prefix quickly. Ranking decides which suggestions are useful. Strong answers keep those responsibilities separate.

## Requirements and constraints

- Clarify ranking: frequency, recency, lexicographic tie-break, personalization, or business score.
- Query returns top `k` suggestions for the current prefix.
- Insert or update a sentence when the user submits it.
- Avoid scanning the whole dictionary on every keystroke.
- Bound memory if storing top suggestions at every node.

## Recognition cue

"Autocomplete", "typeahead", "top suggestions by prefix", and "incremental input" point to trie plus ranking metadata.

## Invariant or state definition

Each prefix node can either point to candidate terminal words in its subtree or store a precomputed top-k list. The ranking source of truth must update whenever a sentence count changes.

## High-level design / approach

Two common designs:

1. **Lazy ranking:** trie node leads to subtree; query DFS collects candidates and ranks them. Simpler, slower for hot prefixes.
2. **Precomputed top-k:** every node stores top candidates for that prefix. Query is fast, insert/update touches every prefix node.

For interviews, choose based on query/write ratio. Read-heavy autocomplete usually precomputes capped top suggestions per prefix.

## Dry run

Sentences:

| Sentence | Count |
|---|---:|
| `i love you` | 5 |
| `island` | 3 |
| `i love leetcode` | 2 |

Query prefix `i` returns candidates from the `i` node. Query prefix `i ` narrows to sentences beginning with `i `, so `island` drops out.

## Language-neutral pseudocode

```text
insert(sentence, delta):
    counts[sentence] += delta
    node = root
    for char in sentence:
        node = node.children.get_or_create(char)
        update_top_k(node.suggestions, sentence, counts[sentence])
    mark terminal

input(char):
    if char == end_marker:
        insert(current_prefix, 1)
        current_prefix = ""
        current_node = root
        return []
    current_prefix += char
    current_node = current_node.children.get(char) if current_node else null
    if current_node == null:
        return []
    return current_node.suggestions
```

## Complexity proof

With precomputed top-k lists, query per character is `O(1)` or `O(k)` after moving one trie edge. Insert/update costs `O(L * updateTopK)` for sentence length `L`. Memory is trie size plus capped suggestion metadata at prefix nodes.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Separation | Separates prefix lookup from ranking |
| Ranking | Defines count and tie-break behavior |
| Read/write trade-off | Chooses lazy or precomputed based on workload |
| Memory | Caps top-k lists and discusses large dictionaries |
| Production transfer | Mentions freshness, abuse, personalization, and metrics |

## Common pitfalls

1. Using trie traversal alone and forgetting ranking.
2. Sorting every sentence after every keystroke.
3. Storing unbounded candidate lists at each node.
4. Failing to update suggestions after count changes.
5. Ignoring spaces or non-letter characters.

## Follow-up questions

1. How would you personalize suggestions?
2. How would you handle trending terms that change quickly?
3. How would you shard autocomplete across machines?
4. How would you protect against spammy injected suggestions?

## Variants and extensions

- Command palette autocomplete.
- URL path suggestions.
- Search query suggestions.
- Prefix index plus ML ranking.

## Cross-links

- [Trie Overview](./01-overview.md)
- [Map Sum Pairs](./05-map-sum-pairs.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
- [Elasticsearch](../../03-hld-concepts/elasticsearch/THEORY.md)
