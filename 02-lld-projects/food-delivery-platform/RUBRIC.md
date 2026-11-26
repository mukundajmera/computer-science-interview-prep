# Interview Rubric: Food Delivery Platform

*Note: This rubric assumes a 45-minute interview pacing.*

*This rubric evaluates behavior and defensible trade-offs rather than buzzwords.*

## 1. Problem Clarification
-   **L6/L7 (Staff/Senior Staff)**: Asks about concurrent state updates, driver assignment criteria, and factors affecting surge pricing. Proposes an optional failure trace with assumptions on network partitions or driver drop-offs.
-   **L5 (Senior)**: Clarifies basic entities and asks about the trade-offs of different dispatch strategies (e.g., Euclidean vs Geohash vs real route distance) and their latency impacts.
-   **L4 (Mid-level)**: Provides an intuitive minimum working solution clarifying basic entities (restaurants, users, drivers). Dives into coding after defining the core workflows.

## 2. System Design & Architecture
-   **L6/L7 (Staff/Senior Staff)**: Uses appropriate design patterns (Strategy for dispatch/pricing, State for orders) and provides a highly defensive, extensible architecture capable of simulating production load.
-   **L5 (Senior)**: Uses appropriate design patterns and articulates trade-offs of separation of concerns between cart, order, and dispatch.
-   **L4 (Mid-level)**: Basic object-oriented modeling. May have a monolithic manager class or slightly coupled logic, but creates an intuitive minimum structure.

## 3. Core Logic (State & Dispatch)
-   **L6/L7 (Staff/Senior Staff)**: Robust order state machine preventing invalid transitions with detailed recovery behaviors. Efficient driver dispatch mechanism that addresses spatial data at scale.
-   **L5 (Senior)**: Implements state machine with defensible trade-offs. Logical driver dispatch mechanism considering spatial data correctly.
-   **L4 (Mid-level)**: Simple state transitions. Basic first-available driver dispatch or naive O(N) matching.

## 4. Code Quality & Concurrency
-   **L6/L7 (Staff/Senior Staff)**: Clean, readable, well-structured code. Thread-safe order state updates and driver assignment (handling race conditions where two orders might try to claim the same driver with advanced locking or atomic references).
-   **L5 (Senior)**: Clean, readable code. Basic concurrency controls applied (e.g., `threading.Lock` or `synchronized`) with an understanding of performance bottlenecks.
-   **L4 (Mid-level)**: Functional code that solves the intuitive minimum problem, but lacks complete concurrency controls.
