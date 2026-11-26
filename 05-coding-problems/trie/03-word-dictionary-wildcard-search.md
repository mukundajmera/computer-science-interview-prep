# Word Dictionary Wildcard Search

## Overview

Design a word dictionary with `addWord(word)` and `search(pattern)`, where `.` matches any single character.

This extends a basic trie with controlled DFS branching. Fixed characters follow one child; wildcard characters branch over all children.

## Requirements and constraints

- `.` matches exactly one character, not zero or many.
- Search length is fixed by the pattern length.
- Words may share prefixes.
- Clarify alphabet size because wildcard branching depends on child count.
- Avoid scanning every word for every wildcard query.

## Recognition cue

The phrase "word dictionary" plus "dot wildcard" suggests a trie with recursive search.

## Invariant or state definition

At recursion index `i`, the current node represents the prefix matched by `pattern[0:i]`. A successful match at the end requires `node.is_word`.

## High-level design / approach

1. Add words exactly like a basic trie.
2. Search recursively with `(node, index)`.
3. If current pattern char is fixed, follow that child only.
4. If current char is `.`, try every child.
5. At `index == len(pattern)`, return whether the node is terminal.

## Dry run

Dictionary: `bad`, `dad`, `mad`.

| Pattern | Search path | Result |
|---|---|---:|
| `pad` | `p` child missing | false |
| `bad` | fixed path `b-a-d` terminal | true |
| `.ad` | branch first char; `b-a-d` works | true |
| `b..` | `b` fixed, then wildcard branches to `a`, then `d` | true |

## Language-neutral pseudocode

```text
search(pattern):
    return dfs(root, 0)

dfs(node, index):
    if index == len(pattern):
        return node.is_word

    char = pattern[index]
    if char != ".":
        if char not in node.children:
            return false
        return dfs(node.children[char], index + 1)

    for child in node.children.values:
        if dfs(child, index + 1):
            return true
    return false
```

## Complexity proof

Without wildcards, search is `O(L)`. With wildcards, worst-case time can branch over many children and approach the number of nodes at matching depths. Space is recursion depth `O(L)`. The trie still avoids exploring prefixes that cannot match the pattern.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Wildcard semantics | Treats `.` as exactly one character |
| Base case | Requires terminal marker at pattern end |
| Branching | Branches only on wildcard positions |
| Complexity | States worst-case branching honestly |
| Pruning | Fails fixed missing children immediately |

## Common pitfalls

1. Treating `.` like regex `.*`.
2. Returning true at the end of a prefix that is not a word.
3. Continuing search after one branch succeeds.
4. Copying substrings on every recursion.
5. Claiming all searches are always `O(L)` despite wildcard branching.

## Follow-up questions

1. How would you support `*` for zero or more characters?
2. How would you cache repeated wildcard searches?
3. What if patterns can be very long?
4. How would you limit abuse from all-wildcard queries?

## Variants and extensions

- Regex-lite dictionary matching.
- Prefix wildcard with bounded depth.
- Search service query guardrails.
- Trie plus memoization for repeated patterns.

## Cross-links

- [Implement Trie](./02-implement-trie-prefix-tree.md)
- [Word Search II](./06-word-search-ii.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
