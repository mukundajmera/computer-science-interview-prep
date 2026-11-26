# Group Shifted Strings

- Canonical ID: `lc-0249-group-shifted-strings`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Group strings that share the same cyclic character-shift pattern.

## Driver Signature

- Java: `List<List<String>> groupStrings(String[] strings)`
- Python: `groupStrings(strings: List[str]) -> List[List[str]]`

## Key Cases and Invariants

- Normalizing each string relative to its first character makes shifted variants equal.
- Singleton strings all share the empty pattern.

## Solution Ladder

### Tier 1: Pairwise assign

Compare each ungrouped string with later strings using cyclic differences.

- Time: `O(n^2 L)` - Pairs can compare up to L characters.
- Space: `O(n)` - Visited flags and output groups are stored.

### Tier 2: Normalized key

Build a canonical key from character offsets relative to the first char.

- Time: `O(nL)` - Each string contributes one key built from its characters.
- Space: `O(nL)` - Keys and output groups store the input strings.
