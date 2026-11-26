# Code Walkthrough: Distributed Unique ID Generator (Snowflake)

This document provides a walkthrough of the `v1-basic` implementation of the Snowflake ID generator for both Java and Python.

## Core Snowflake Implementation

The core algorithm is implemented in `SnowflakeGenerator.java` and `snowflake_generator.py`. The generation logic relies on constructing a 64-bit integer by bitwise shifting and ORing three components:
1. **Timestamp (41 bits):** The difference between the current time and a custom epoch in milliseconds.
2. **Worker ID (10 bits):** A unique identifier for the machine generating the ID.
3. **Sequence (12 bits):** A local counter that increments for IDs generated within the same millisecond.

```java
// Java snippet
return ((timestamp - epoch) << TIMESTAMP_LEFT_SHIFT)
        | (workerId << WORKER_ID_SHIFT)
        | sequence;
```

If the sequence counter exceeds its maximum value (4095) within a given millisecond, the generator blocks (sleep-wait) until the clock ticks to the next millisecond.

## Clock Dependency Injection

To make the algorithm testable, the system clock is abstracted into a `Clock` interface (Java) / abstract class (Python). The production code uses `SystemClock`, which delegates to the actual system time, whereas the test code injects a `MockClock` to simulate time advancing or moving backwards.

## Failure Handling: NTP Backward Clock Shifts

The system explicitly checks for backwards clock shifts. If the current time is less than the last timestamp used, a `ClockMovedBackwardsException` is thrown, adhering to the fail-fast constraint defined in `DESIGN.md`.

## Testing Simplifications (`v1-basic`)

To isolate the core ID generation logic, `v1-basic` makes several test simplifications:
- **Mocked Clock:** Instead of relying on volatile system time, tests inject a `MockClock` to deterministically verify sequence rollover and backward clock shift failures.
- **In-Memory Transport:** Real distributed transport mechanisms (e.g., gRPC, REST) are entirely mocked out. Tests invoke the generator locally.
- **Security Omitted:** Internal service-to-service authentication (e.g., mTLS) is skipped.
- **ZooKeeper Omitted:** The dynamic leasing and assignment of Worker IDs are mocked by simply instantiating generators with hardcoded worker IDs in tests.
