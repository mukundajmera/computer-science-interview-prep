# Logger Rate Limiter

- Canonical ID: `lc-0359-logger-rate-limiter`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Design a logger that allows a message to print only if the same message has not printed in the previous ten seconds.

## Driver Signature

- Java class: `Logger`
- Python class: `Logger`
- Methods: `['shouldPrintMessage']`

## Key Cases and Invariants

- Different messages are tracked independently.
- A message becomes printable again at exactly last printed timestamp plus ten.

## Solution Ladder

### Tier 1: History scan

Keep printed events and scan backward for a recent matching message.

- Time: `O(n)` - A call may scan all prior printed events.
- Space: `O(n)` - Printed events are retained.

### Tier 2: Next allowed map

Map each message to the earliest timestamp where it can print again.

- Time: `O(1)` - Each call does constant map work.
- Space: `O(m)` - The map stores one entry per message.
