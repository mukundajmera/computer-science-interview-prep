# Replace Words

## Overview

Given a dictionary of root words and a sentence, replace each word with the shortest dictionary root that is a prefix of the word.

A trie fits because each sentence word can stop as soon as it reaches the first terminal node.

## Requirements and constraints

- Replace with the shortest root, not any root.
- Preserve words with no matching root.
- Split and join sentence tokens according to the prompt's whitespace rules.
- Clarify lowercase-only input.
- Dictionary roots may share prefixes.

## Recognition cue

"Shortest root prefix" is a direct trie signal because the first terminal node on a word path wins.

## Invariant or state definition

During traversal of a sentence word, the first terminal node reached represents the shortest valid replacement root.

## High-level design / approach

1. Insert every root into a trie.
2. For each sentence word:
   - walk characters from the root;
   - if a child is missing, keep the original word;
   - if a terminal node is reached, return the prefix so far.
3. Join transformed words back into a sentence.

## Dry run

Roots: `cat`, `bat`, `rat`.

Sentence: `the cattle was rattled by the battery`.

| Word | Traversal | Replacement |
|---|---|---|
| `the` | `t` missing | `the` |
| `cattle` | `c-a-t` terminal | `cat` |
| `rattled` | `r-a-t` terminal | `rat` |
| `battery` | `b-a-t` terminal | `bat` |

Output: `the cat was rat by the bat`.

## Language-neutral pseudocode

```text
build trie from roots

replace(word):
    node = root
    prefix = []
    for char in word:
        if char not in node.children:
            return word
        node = node.children[char]
        prefix.append(char)
        if node.is_word:
            return join(prefix)
    return word

answer = [replace(word) for word in sentence_words]
```

## Complexity proof

Building the trie costs `O(total_root_chars)`. Replacing a word costs at most `O(L)`, but often stops early at the shortest root. Extra space is the trie plus output tokens.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Shortest root | Stops at the first terminal node |
| No match | Preserves original word |
| Token handling | Keeps sentence reconstruction simple |
| Complexity | Separates build cost and sentence scan cost |
| Edge cases | Handles root that equals full word and roots sharing prefixes |

## Common pitfalls

1. Returning the longest matching root.
2. Continuing traversal after the first terminal root.
3. Dropping words that have no replacement.
4. Rebuilding the trie for every sentence word.
5. Breaking punctuation behavior without clarifying input rules.

## Follow-up questions

1. How would you handle punctuation and case?
2. How would this change for streaming text?
3. How would you support root deletion?
4. When would a hash set of prefixes be acceptable?

## Variants and extensions

- URL prefix rewrite.
- Command alias expansion.
- Search query normalization.
- Dictionary root replacement with audit logging.

## Cross-links

- [Trie Overview](./01-overview.md)
- [Autocomplete System](./07-design-search-autocomplete-system.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
