# Problem: High-Concurrency Striped Counter

Design and implement a highly concurrent striped counter (local state). The system needs to track the sum of items/events in a multi-threaded application. Note: This is not a network-distributed counter.

## Requirements
- Support an `increment()` method that adds 1 to the counter.
- Support an `increment(x)` method that adds `x` to the counter.
- Support a `get()` method that retrieves the aggregate sum.
- Ensure thread safety without suffering from severe lock contention under high concurrency.
- **v1-basic:** A simple globally locked counter (preserves exact AtomicLong/locked baseline).
- **v2-extended:** A counter striped across a fixed-size array of cells.
- **v3-optimized:** A highly concurrent counter that dynamically resizes its cell array based on contention and CPU count, using probe hashing to minimize lock collisions.

## Acceptance Criteria
- A completed fixed update set sums exactly after quiescence; concurrent striped sum is labeled non-atomic and never used for strict quota decisions.
- Overflow, negative-update policy, shard lifecycle and contention histories preserve the documented local—not network-distributed—counter contract.
- Version-specific APIs and deterministic fixture inputs/expected outputs are fixed before implementation; no production/security promise is inferred.
