# Single-Row Keyboard

- Canonical ID: `lc-1165-single-row-keyboard`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Given a keyboard layout string and a word, compute the total finger travel distance while typing the word from index 0.

## Driver Signature

- Java: `int calculateTime(String keyboard, String word)`
- Python: `calculateTime(keyboard: str, word: str) -> int`

## Key Cases and Invariants

- Each keyboard character has one position.
- Travel cost is the absolute distance from the previous position.

## Solution Ladder

### Tier 1: Index search

Find each character's index in the keyboard string as it is typed.

- Time: `O(kw)` - Each of w word chars can scan k keyboard chars.
- Space: `O(1)` - Only the current position is stored.

### Tier 2: Position map

Precompute character positions and sum absolute movement.

- Time: `O(k + w)` - Build positions once and scan the word once.
- Space: `O(k)` - The position table stores one entry per keyboard character.
