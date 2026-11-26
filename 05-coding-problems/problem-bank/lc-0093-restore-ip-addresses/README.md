# Restore IP Addresses

- Canonical ID: `lc-0093-restore-ip-addresses`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Split a digit string into all valid four-part IPv4-style addresses.

## Driver Signature

- Java: `List<String> restoreIpAddresses(String s)`
- Python: `restoreIpAddresses(s: str) -> List[str]`

## Key Cases and Invariants

- Each part must be between 0 and 255.
- A multi-digit part cannot start with zero.

## Solution Ladder

### Tier 1: Enumerate split lengths

Try all three possible lengths for each of the four address parts.

- Time: `O(1)` - At most 3^4 split patterns are inspected.
- Space: `O(1)` - The recursion depth and candidate part count are bounded by four.

### Tier 2: Backtracking with remaining-length pruning

Prune when remaining digits cannot fill the remaining parts.

- Time: `O(1)` - The bounded IPv4 search space is constant, with fewer invalid branches explored.
- Space: `O(1)` - Only four parts are stored.
