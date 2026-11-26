# Coach Answer: Coding Trie Pack

> Type: Coding Pattern Drill
> Difficulty: Intermediate
> Time Target: 45 minutes

## Phase 1 - Problem Framing

Strong candidates do not say "use a trie" and stop. They define the prefix contract.

1. Identify whether the operation is exact word lookup, prefix lookup, wildcard search, prefix aggregate, board pruning, or autocomplete.
2. Define the trie node: child representation, terminal marker, and optional metadata.
3. Clarify alphabet and normalization.
4. State the invariant: the root-to-node path is the current prefix.
5. Separate word existence from prefix existence.
6. Add metadata only when the prompt needs it.
7. Explain memory trade-offs before claiming scale readiness.

## Phase 2 - Canonical Templates

### Template A: Basic Trie

```text
insert(word):
    node = root
    for char in word:
        node = node.children.get_or_create(char)
    node.is_word = true

search(word):
    node = walk(word)
    return node exists and node.is_word
```

Use for exact and prefix lookup.

### Template B: Wildcard DFS

```text
dfs(node, i):
    if i == len(pattern): return node.is_word
    if pattern[i] is fixed:
        return child exists and dfs(child, i + 1)
    for child in node.children:
        if dfs(child, i + 1): return true
    return false
```

Use when one pattern character can match many trie children.

### Template C: Prefix Aggregate

```text
delta = new_value - old_value
for node on key path:
    node.sum += delta
```

Use when prefix queries need counts, sums, or bounded top candidates.

### Template D: Trie Plus Board DFS

```text
dfs(cell, trie_node):
    if board char not in trie_node.children: return
    move to child
    emit word if terminal
    mark cell, visit neighbors, unmark cell
```

Use when dictionary prefixes prune a grid search.

## Phase 3 - Problem-by-Problem Walkthrough

1. **Implement Trie / Prefix Tree**
   - State: child map plus terminal marker.
   - Core distinction: prefix path exists vs exact word is terminal.

2. **Word Dictionary Wildcard Search**
   - State: recursive `(node, index)`.
   - Fixed char follows one edge; dot branches over children.

3. **Replace Words**
   - State: dictionary roots in a trie.
   - First terminal node is the shortest replacement.

4. **Map Sum Pairs**
   - State: trie prefix sums plus key-to-value map.
   - Overwrite uses delta.

5. **Word Search II**
   - State: board DFS path and current trie node.
   - Trie prefix miss prunes the branch.

6. **Design Search Autocomplete System**
   - State: prefix node plus ranked candidate metadata.
   - Prefix lookup and ranking are separate responsibilities.

7. **Longest Word in Dictionary**
   - State: terminal-prefix-only DFS.
   - Every prefix on the answer path must be a word.

## Phase 4 - Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Node contract | 20% | Defines children, terminal marker, and metadata |
| Semantics | 20% | Separates exact word, prefix, wildcard, and aggregate behavior |
| Invariant | 20% | Explains root-to-node prefix meaning |
| Edge cases | 15% | Handles prefix-as-word, duplicates, missing child, overwrite, and dedupe |
| Complexity | 15% | Uses word length, total characters, branching, and memory overhead |
| Transfer | 10% | Connects prefix lookup to ranking, freshness, and storage trade-offs |

## Phase 5 - Common Pitfalls

1. Treating any prefix path as a word.
2. Forgetting terminal markers.
3. Claiming wildcard search is always linear.
4. Rebuilding tries per query.
5. Updating prefix sums without subtracting old values.
6. Returning duplicate board words.
7. Storing unbounded autocomplete candidates at every node.
8. Calling trie autocomplete a full search engine.

## System Design Transfer Script

| Trie concept | Production analogue | Scale risk | Validation signal |
|---|---|---|---|
| Prefix path | typeahead prefix, route path, command prefix | large alphabet, memory overhead | prefix lookup latency |
| Terminal marker | valid command or dictionary term | stale or deleted terms | correctness audit |
| Prefix aggregate | counters, popularity, quotas | write amplification | freshness lag |
| Top suggestions | autocomplete candidates | duplicated metadata | click-through, selection rate |
| Wildcard branch | flexible query matching | query explosion | timeout and branch-count metrics |

## Follow-Up Drill Set

1. Implement Trie.
2. Word Dictionary wildcard search.
3. Replace Words.
4. Map Sum Pairs.
5. Word Search II.
6. Autocomplete with top-3 suggestions.
7. Longest Word in Dictionary.
8. Prefix route matching for service endpoints.

## Cross-links

- [Trie Pattern Pack](../05-coding-problems/trie/README.md)
- [Trie Quiz](../quizzes/trie-quiz.md)
- [Trie Flashcards](../flashcards/trie.md)
- [Search Systems](../03-hld-concepts/search-systems/THEORY.md)
- [Elasticsearch](../03-hld-concepts/elasticsearch/THEORY.md)
