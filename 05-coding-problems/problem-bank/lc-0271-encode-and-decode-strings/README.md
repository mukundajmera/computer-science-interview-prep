# Encode and Decode Strings

- Canonical ID: `lc-0271-encode-and-decode-strings`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Design a reversible codec for a list of strings so arbitrary characters, empty strings, and delimiter-looking content can be encoded into one string and decoded exactly.

## Driver Signature

- Java class: `Codec`
- Python class: `Codec`
- Constructor parameters: `[]`
- Methods: `['encode', 'decode']`

## Key Cases and Invariants

- A delimiter alone is unsafe because input strings may contain that delimiter.
- Length prefixes make decoding unambiguous.
- Empty strings must round-trip as real list elements.

## Solution Ladder

### Tier 1: Length prefix

Prefix each string with its decimal length and a separator that is read only after the length.

- Time: `O(N)` - Encoding and decoding scan the total character count once.
- Space: `O(N)` - The encoded string and decoded list store the full payload.

### Tier 2: Indexed length prefix

Use the same format with explicit index movement to keep decode iterative and allocation-light.

- Time: `O(N)` - Each encoded character belongs to exactly one parse step.
- Space: `O(N)` - Output storage is linear in payload size.
