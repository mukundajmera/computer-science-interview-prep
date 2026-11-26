# Reorganize String

## Overview

Given a string, rearrange characters so no two adjacent characters are the same. Return any valid string, or an empty string if impossible.

The heap approach repeatedly chooses the highest remaining count character that is not equal to the previous character. A held-back previous character is reinserted only after a different character is placed.

## Requirements and constraints

- Adjacent equal characters are not allowed.
- Any valid arrangement is acceptable unless the prompt specifies ordering.
- If the largest frequency is greater than `(n + 1) / 2`, no valid arrangement exists.
- Track characters and counts, not just counts, because output matters.

## Recognition cue

"Rearrange characters", "no adjacent same", and "use the most frequent remaining item safely" signal a max-heap with delayed reinsert.

## Invariant or state definition

The heap contains characters that are eligible for the current position. The previously used character is held out for one step if it still has remaining count, preventing immediate reuse.

## High-level design / approach

1. Count character frequencies.
2. If any count exceeds `(len(s) + 1) / 2`, return empty string.
3. Push `(count, char)` entries into a max-heap.
4. Track `prev` as the character just used with remaining count.
5. At each step, pop the highest-count eligible character, append it, decrement it, then reinsert `prev` if it still has count.
6. Set current character as the new `prev` if it still has count.

## Dry run

String: `aaabbc`.

| Step | Pick | Output | Held out after step | Heap summary |
|---:|---|---|---|---|
| 1 | a | `a` | a2 | b2, c1 |
| 2 | b | `ab` | b1 | a2, c1 |
| 3 | a | `aba` | a1 | b1, c1 |
| 4 | b | `abab` | none | a1, c1 |
| 5 | a | `ababa` | none | c1 |
| 6 | c | `ababac` | none | empty |

The result has no adjacent equal characters.

## Language-neutral pseudocode

```text
if s is empty:
    return ""
counts = frequency_map(s)
if max(counts.values) > (length(s) + 1) / 2:
    return ""

heap = max_heap of (count, char)
prev = none
answer = []
while heap not empty:
    count, char = heap.pop_max()
    answer.append(char)
    count -= 1

    if prev is not none and prev.count > 0:
        heap.push(prev)

    prev = (count, char) if count > 0 else none

return join(answer)
```

## Complexity proof

Counting costs `O(n)`. Each character placement performs at most one pop and one push over `U` unique characters, so time is `O(n log U)`. Space is `O(U)` for counts and heap, plus `O(n)` for output.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Impossibility | Checks maximum frequency bound |
| Eligibility | Prevents immediate reuse of previous character |
| Heap entry | Stores both count and character |
| Output | Builds exactly length `n` when possible |
| Complexity | Uses unique character count `U` |

## Common pitfalls

1. Reinsert the same character before choosing the next character.
2. Forget the impossibility bound.
3. Pop two characters at a time and mishandle odd leftover counts.
4. Return partial output when heap becomes empty but held character remains.
5. Ignore deterministic tie behavior in tests.

## Follow-up questions

1. What changes for distance `k` apart instead of no adjacent duplicates?
2. How would you return the lexicographically smallest valid answer?
3. How does this relate to Task Scheduler?
4. What if the alphabet is very large?

## Variants and extensions

- Rearrange barcodes.
- K-distance apart strings.
- Cooldown scheduling.
- Fair queue dispatch across tenants.

## Cross-links

- [Heap / Priority Queue Overview](./01-overview.md)
- [Task Scheduler](./06-task-scheduler.md)
- [Message Queues](../../03-hld-concepts/message-queues/THEORY.md)
