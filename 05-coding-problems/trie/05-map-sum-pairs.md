# Map Sum Pairs

## Overview

Design a map that supports `insert(key, value)` and `sum(prefix)`, returning the sum of all values whose keys start with `prefix`.

The trie stores prefix aggregates. The hard part is updates: inserting an existing key must adjust every prefix by the delta between new and old value.

## Requirements and constraints

- `insert` overwrites existing key values.
- `sum(prefix)` returns `0` when the prefix does not exist.
- Keys are strings; values are integers.
- Clarify negative values if relevant.
- Prefix query should be faster than scanning every key.

## Recognition cue

"Sum of all values with a prefix" means prefix traversal plus metadata at each prefix node.

## Invariant or state definition

Each trie node stores the total value of all complete keys in its subtree. A separate hash map stores the current value for each full key so updates can compute a delta.

## High-level design / approach

1. Keep `values[key] = current_value`.
2. On insert, compute `delta = new_value - old_value`.
3. Walk or create trie nodes for the key.
4. Add `delta` to every node on the path.
5. For `sum(prefix)`, walk to the prefix node and return its stored sum.

## Dry run

Operations:

```text
insert("apple", 3)
sum("ap") -> 3
insert("app", 2)
sum("ap") -> 5
insert("apple", 2)
sum("ap") -> 4
```

The last insert has `delta = -1`, so every prefix on `apple` decreases by one.

## Language-neutral pseudocode

```text
insert(key, value):
    delta = value - values.get(key, 0)
    values[key] = value
    node = root
    node.sum += delta
    for char in key:
        node = node.children.get_or_create(char)
        node.sum += delta

sum(prefix):
    node = walk(prefix)
    if node == null:
        return 0
    return node.sum
```

## Complexity proof

`insert` costs `O(L)` for key length `L` and updates one node per character. `sum` costs `O(P)` for prefix length `P`. Space is trie nodes plus one hash map entry per key.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Update handling | Uses delta for overwrites |
| Prefix metadata | Stores aggregate at every prefix node |
| Query speed | Returns prefix-node sum without subtree scan |
| Edge cases | Handles missing prefix and key overwrite |
| Complexity | States key-length and prefix-length costs |

## Common pitfalls

1. Adding the full value again on overwrite.
2. Storing sums only at terminal nodes and scanning descendants on every query.
3. Forgetting the root if empty prefix sums are allowed.
4. Losing negative deltas.
5. Not keeping the separate key-value map.

## Follow-up questions

1. How would deletes work?
2. How would you support top-k keys per prefix?
3. How would large values or overflow affect the design?
4. How would you shard this service by prefix?

## Variants and extensions

- Prefix counters.
- Autocomplete frequency aggregates.
- Metrics grouped by hierarchical key.
- Path-prefix quota tracking.

## Cross-links

- [Implement Trie](./02-implement-trie-prefix-tree.md)
- [Autocomplete System](./07-design-search-autocomplete-system.md)
- [Realtime Metrics Platform](../../04-hld-projects/realtime-metrics-platform/)
