# Maximum Frequency Stack

- Canonical ID: `lc-0895-maximum-frequency-stack`
- Difficulty: `hard`
- Status: `verified`

## Clean-Room Problem Summary

Design a stack-like structure where pop removes the value with highest frequency; ties are resolved by most recent push among tied values.

## Driver Signature

- Java class: `FreqStack`
- Python class: `FreqStack`
- Constructor parameters: `[]`
- Methods: `['push', 'pop']`

## Key Cases and Invariants

- Frequency is updated after every push and pop.
- Recency only matters among values with the same current frequency.
- A stack per frequency gives direct access to the newest value at the current maximum frequency.

## Solution Ladder

### Tier 1: Scan stack

Keep the full push stack and frequencies, scanning backward on pop for the newest max-frequency value.

- Time: `O(n)` - A pop may scan the full stack.
- Space: `O(n)` - The stack and frequency map retain live pushes.

### Tier 2: Frequency stacks

Map each frequency to a stack of values that reached it and track the current maximum frequency.

- Time: `O(1)` - Push and pop update constant-time maps/stacks.
- Space: `O(n)` - Every push is represented in one frequency stack.
