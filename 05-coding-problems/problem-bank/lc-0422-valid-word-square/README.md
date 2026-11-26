# Valid Word Square

- Canonical ID: `lc-0422-valid-word-square`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Determine whether the row strings read the same as the column strings wherever characters exist.

## Driver Signature

- Java: `boolean validWordSquare(List<String> words)`
- Python: `validWordSquare(words: List[str]) -> bool`

## Key Cases and Invariants

- Rows can have different lengths.
- Every existing row character must have a matching column character, and missing counterparts make the square invalid.

## Solution Ladder

### Tier 1: Build columns

Construct every column string and compare it with the corresponding row string.

- Time: `O(nm)` - Every character is copied into a column.
- Space: `O(nm)` - Column strings can store all characters.

### Tier 2: Direct symmetry check

For each row character, directly verify the mirrored column position exists and matches.

- Time: `O(nm)` - Each existing character is checked once.
- Space: `O(1)` - Only loop variables are stored.
