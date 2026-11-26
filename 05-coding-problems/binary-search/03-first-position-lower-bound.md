# First Position / Lower Bound

## Overview

Given a sorted array that may contain duplicates, return the first index where `nums[i] >= target`. If the prompt asks for the first occurrence of `target`, return that index only when `nums[index] == target`; otherwise return `-1`.

Lower bound is the most reusable binary-search template because it finds a boundary, not just an exact match.

## Requirements and constraints

- Input is sorted in ascending order.
- Duplicates may exist.
- Return the smallest index satisfying the predicate.
- For first occurrence, verify the value after the loop.
- Prefer `O(log n)` time and `O(1)` space.

## High-level design / approach

1. Use a half-open search range: `left = 0`, `right = n`.
2. Predicate: `nums[mid] >= target`.
3. While `left < right`:
   - compute `mid`;
   - if the predicate is true, keep `mid` as a candidate by setting `right = mid`;
   - otherwise set `left = mid + 1`.
4. At loop end, `left` is the first index where the predicate could be true.
5. For first occurrence, return `left` only if `left < n` and `nums[left] == target`.

Invariant: all indices before `left` are known to be too small; all indices at or after `right` remain possible first-true candidates.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Boundary framing | Describes first true / lower-bound semantics |
| Duplicate handling | Keeps searching left after a match candidate |
| Return validation | Distinguishes insertion point from actual occurrence |
| Termination | Uses half-open `left < right` with progress every iteration |

## Common pitfalls

1. Returning as soon as `nums[mid] == target`, which may miss an earlier duplicate.
2. Setting `right = mid - 1` and discarding the candidate boundary.
3. Failing when every value is less than the target.
4. Failing when every value is greater than or equal to the target.

## Follow-up questions

1. How would you find the last occurrence?
2. How do lower bound and upper bound combine to count duplicates?
3. How does this map to finding the first log timestamp at or after a cursor?

## Variants and extensions

- Count occurrences with `upper_bound(target) - lower_bound(target)`.
- Find the first bad version in a release sequence.
- Find the first event whose timestamp is at least a requested start time.
- Locate the first shard/ring node whose token is greater than or equal to a key hash.

## Cross-links

- [Classic Binary Search](./02-classic-binary-search.md)
- [Search Insert Position](./04-search-insert-position.md)
- [HLD Consistent Hashing](../../03-hld-concepts/consistent-hashing/THEORY.md)
- [HLD API Design](../../03-hld-concepts/api-design/THEORY.md)
