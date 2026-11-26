# Serialize and Deserialize Binary Tree

- Canonical ID: `lc-0297-serialize-and-deserialize-binary-tree`
- Difficulty: `hard`
- Status: `verified`

## Clean-Room Problem Summary

Design a codec that converts a binary tree into a string and reconstructs the same tree shape and values from that string.

## Driver Signature

- Java class: `Codec`
- Python class: `Codec`
- Constructor parameters: `[]`
- Methods: `['serialize', 'deserialize']`

## Key Cases and Invariants

- Null children must be represented so asymmetric trees round-trip correctly.
- The codec format is internal to the implementation as long as serialize and deserialize agree.
- Negative and multi-digit values must not collide with separators.

## Solution Ladder

### Tier 1: Recursive preorder codec

Emit value/null markers in preorder and consume the token stream recursively during decode.

- Time: `O(n)` - Each node and null marker is processed once.
- Space: `O(n)` - The token stream and recursion stack are linear in the tree size.

### Tier 2: Iterative preorder codec

Produce the same preorder format iteratively and decode with an index holder to avoid substring parsing.

- Time: `O(n)` - Serialization and deserialization both traverse the token list once.
- Space: `O(n)` - The token list and stack/index state are linear.
