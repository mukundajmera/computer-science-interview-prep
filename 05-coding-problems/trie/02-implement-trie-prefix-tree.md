# Implement Trie / Prefix Tree

## Overview

Implement `insert`, `search`, and `startsWith`.

This is the canonical trie problem. It tests whether you can separate path existence from complete-word existence and keep each operation proportional to the input string length.

## Requirements and constraints

- `insert(word)` stores a word.
- `search(word)` returns true only when the full word was inserted.
- `startsWith(prefix)` returns true when any inserted word has that prefix.
- Clarify empty strings and allowed characters.
- Duplicate inserts should not break correctness.

## Recognition cue

The method names directly reveal the pattern: exact word lookup and prefix lookup over a dictionary.

## Invariant or state definition

After all inserts, walking from root by the characters of any inserted word reaches a terminal node. Walking by a prefix reaches a node, but that node may or may not be terminal.

## High-level design / approach

1. Define a root node with an empty child map.
2. Insert by creating missing nodes.
3. Mark the last node with `is_word = true`.
4. Use a shared helper `walk(text)` for both queries.
5. `search` checks `walk(word).is_word`; `startsWith` checks only existence.

## Dry run

Operations:

```text
insert("apple")
search("apple")    -> true
search("app")      -> false
startsWith("app")  -> true
insert("app")
search("app")      -> true
```

Before inserting `app`, the node for `app` exists but is not terminal. After inserting it, the same node becomes terminal.

## Language-neutral pseudocode

```text
class Trie:
    root = Node()

    insert(word):
        node = root
        for char in word:
            node = node.children.get_or_create(char)
        node.is_word = true

    walk(text):
        node = root
        for char in text:
            if char not in node.children:
                return null
            node = node.children[char]
        return node

    search(word):
        node = walk(word)
        return node != null and node.is_word

    startsWith(prefix):
        return walk(prefix) != null
```

## Complexity proof

Each operation scans exactly the characters in its argument. Time is `O(L)`. Space added by insertion is at most `O(L)` new nodes, less when prefixes are shared.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| API semantics | Correctly distinguishes `search` and `startsWith` |
| Helper reuse | Uses one traversal helper without conflating terminal logic |
| Data structure | Chooses child map or fixed array intentionally |
| Complexity | States `O(L)` per operation and total-character memory |
| Edge cases | Handles duplicate insert and prefix-as-word |

## Common pitfalls

1. Making `search("app")` true after only inserting `apple`.
2. Failing when the same word is inserted twice.
3. Returning false for empty prefix when the API should accept it.
4. Using substring copies in recursion and turning `O(L)` into extra allocation.
5. Assuming all child slots exist and dereferencing missing children.

## Follow-up questions

1. How would you implement delete?
2. What changes if the alphabet is fixed at 26 lowercase letters?
3. How would you count how many words share a prefix?
4. How would you serialize this trie?

## Variants and extensions

- Prefix count trie.
- Compressed trie for memory reduction.
- Trie over tokens for command or route matching.
- Case-insensitive dictionary search.

## Cross-links

- [Trie Overview](./01-overview.md)
- [Map Sum Pairs](./05-map-sum-pairs.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
