# Trie Overview

## Overview

A trie turns a dictionary into a prefix graph. Instead of scanning every word for every query, you consume one character at a time and either keep moving through matching children or fail immediately.

The core interview move is to state the node contract before coding:

```text
node.children: map from character to child node
node.is_word: whether this prefix is a complete stored word
optional node metadata: count, sum, top suggestions, word reference
```

## Requirements and constraints

- Define whether characters are lowercase English letters, arbitrary ASCII, or Unicode.
- Clarify duplicate insert behavior.
- Separate exact word search from prefix search.
- State expected query volume; tries help most when many queries reuse the same dictionary.
- Call out memory: sparse maps are flexible, arrays are faster for small fixed alphabets.

## Recognition cue

The cue is any repeated question shaped like "does this prefix exist", "which words start with this", or "can this partial path still become a dictionary word."

## Invariant or state definition

For every stored word, every prefix of that word maps to a path from the root. A terminal marker records which prefixes are complete words.

## High-level design / approach

1. Start at the root.
2. For insertion, create missing child nodes for each character.
3. Mark the final node as terminal.
4. For exact search, walk all characters and require the final node to be terminal.
5. For prefix search, walk all characters and accept if the path exists.
6. Add metadata only when the problem requires it.

## Dry run

Insert `app`, `apple`, and `bat`.

| Step | Node reached | Terminal? | Meaning |
|---|---|---:|---|
| `a` | prefix `a` | no | a prefix exists |
| `ap` | prefix `ap` | no | a prefix exists |
| `app` | prefix `app` | yes | `app` is a word |
| `appl` | prefix `appl` | no | only a prefix |
| `apple` | prefix `apple` | yes | `apple` is a word |

`startsWith("app")` is true. `search("appl")` is false.

## Language-neutral pseudocode

```text
insert(word):
    node = root
    for char in word:
        if char not in node.children:
            node.children[char] = new_node()
        node = node.children[char]
    node.is_word = true

search(word):
    node = walk(word)
    return node exists and node.is_word

starts_with(prefix):
    return walk(prefix) exists
```

## Complexity proof

Insertion, exact search, and prefix search each visit one node per character, so time is `O(L)` for query length `L`. Memory is `O(T * A_overhead)` in practice, where `T` is total stored characters after shared prefixes and `A_overhead` is child representation cost.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Node contract | Defines child map and terminal marker before implementation |
| Search semantics | Distinguishes exact word from prefix |
| Memory | Mentions array vs hash map vs compression trade-off |
| Edge cases | Handles duplicate words, empty prefix, and prefix-as-word |
| Transfer | Explains why prefix lookup is not full-text search |

## Common pitfalls

1. Returning true for exact search when only a prefix exists.
2. Forgetting to mark the terminal node during insert.
3. Assuming 26 lowercase characters without confirming the input.
4. Storing whole words at every node when only terminal flags are needed.
5. Ignoring deletes or updates when metadata is added later.

## Follow-up questions

1. How would you delete a word and clean unused nodes?
2. When would you use a compressed trie?
3. How would you store autocomplete suggestions without unbounded memory?
4. How would Unicode change node representation?

## Variants and extensions

- Radix tree / compressed trie.
- Suffix trie for substring-heavy workloads.
- Trie plus heap or ranker for autocomplete.
- Trie over URL path segments instead of characters.

## Cross-links

- [Trie Pattern Pack](./README.md)
- [Wildcard Search](./03-word-dictionary-wildcard-search.md)
- [Autocomplete System](./07-design-search-autocomplete-system.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
