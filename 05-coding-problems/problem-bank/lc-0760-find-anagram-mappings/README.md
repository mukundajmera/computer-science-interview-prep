# Find Anagram Mappings

- Canonical ID: `lc-0760-find-anagram-mappings`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

For each value in the first array, return an index where that same value appears in the second array.

## Driver Signature

- Java: `int[] anagramMappings(int[] nums1, int[] nums2)`
- Python: `anagramMappings(nums1: List[int], nums2: List[int]) -> List[int]`

## Key Cases and Invariants

- Duplicate values may map to any still-valid matching index.
- A value-to-list-of-indices map handles duplicates deterministically.

## Solution Ladder

### Tier 1: Nested search

For each nums1 value, scan nums2 for the first unused matching index.

- Time: `O(n^2)` - Every value may scan nums2.
- Space: `O(n)` - Used flags track consumed duplicate indices.

### Tier 2: Index queues

Map each value in nums2 to a queue of matching indices, then pop one index per nums1 value.

- Time: `O(n)` - Both arrays are scanned once.
- Space: `O(n)` - Queues store every index of nums2.
