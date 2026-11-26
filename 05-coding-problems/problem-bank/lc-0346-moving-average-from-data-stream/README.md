# Moving Average from Data Stream

- Canonical ID: `lc-0346-moving-average-from-data-stream`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Design a moving-average calculator that returns the average of the last at most `size` inserted values.

## Driver Signature

- Java class: `MovingAverage`
- Python class: `MovingAverage`
- Methods: `['next']`

## Key Cases and Invariants

- Before the window is full, average over all seen values.
- After the window is full, remove the oldest value on each insert.

## Solution Ladder

### Tier 1: List window sum

Keep all values in a list and sum the active suffix for every query.

- Time: `O(k)` - Each next can sum up to k values.
- Space: `O(n)` - All inserted values are retained.

### Tier 2: Queue running sum

Keep only the active window in a queue and maintain its running sum.

- Time: `O(1)` - Each next does constant queue and sum updates.
- Space: `O(k)` - The queue stores at most k values.
