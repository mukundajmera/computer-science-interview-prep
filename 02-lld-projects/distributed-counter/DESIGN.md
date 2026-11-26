# Design

## Counter Contract
- **Non-Atomic Concurrent Sum:** In striped implementations (`v2` and `v3`), a concurrent sum is not an atomic snapshot. It is unsuitable for strict quota limits.
- **Quiescence:** A completed fixed update set sums exactly after quiescence.
- **Local State:** This design preserves local state (not a network-distributed counter contract). Overflow, negative-update policies, and shard lifecycles adhere strictly to this local constraint.

## Architecture

The system consists of a `Counter` class that manages access to underlying `Cell` objects.

```mermaid
classDiagram
    class Counter {
        +increment()
        +increment(x)
        +get()
    }
    class Cell {
        +value: long
        +lock: Lock
    }
    Counter "1" *-- "many" Cell : contains
```

## Flow for v3-optimized

```mermaid
flowchart TD
    Start[Thread calls increment] --> TryBase{Try CAS on Base?}
    TryBase -- Success --> End[Done]
    TryBase -- Contended --> CheckCells{Cells initialized?}
    
    CheckCells -- No --> InitCells[Allocate Cells]
    InitCells --> Hash[Hash Thread Probe to Cell]
    
    CheckCells -- Yes --> Hash
    
    Hash --> TryCell{Try CAS on Cell?}
    TryCell -- Success --> End
    TryCell -- Contended --> ResizeOrRehash[Resize Cells or Rehash Probe]
    ResizeOrRehash --> Hash
```
