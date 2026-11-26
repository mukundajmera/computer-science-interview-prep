# Code Walkthrough: CDN Simulator (v1-basic)

This document provides a walkthrough of the `v1-basic` bounded paired-language simulator for the Content Delivery Network (CDN) implemented in both Java and Python.

## Core Implementations

The implementation simulates the hierarchical caching mechanism of a CDN, directly modeling the components highlighted in the `DESIGN.md`.

- **CustomerOrigin**: Acts as the ultimate source of truth for assets. It tracks the number of times it has been hit (`fetchCount`) to verify cache and coalescing effectiveness.
- **OriginShield**: The regional caching layer that protects the `CustomerOrigin`. It implements **Request Coalescing** to protect against the "Thundering Herd" failure invariant.
- **EdgeNode**: The local PoP (Point of Presence) that first receives user requests, caching data to provide low-latency responses.

## Exact Fixture Matching & Named Failure Invariant

Both Java and Python test suites (`CdnSimulatorTest.java` and `test_cdn_simulator.py`) implement the exact same test cases:

1. **Normal Trace** (`testNormalHit`): Verifies the standard cache-miss and subsequent cache-hit flow. The first request hits the `CustomerOrigin`, and subsequent requests are served from the `EdgeNode` cache, ensuring the origin is not queried again.
2. **Failure Trace: Thundering Herd** (`testThunderingHerdCoalescing`): Simulates 10,000 concurrent requests for an uncached or just-purged asset. By leveraging Request Coalescing in the `OriginShield`, the implementation guarantees that exactly **one** request reaches the `CustomerOrigin`, successfully protecting it while delivering the asset to all 10,000 requests.

## Simplifications

To create a focused, deterministic in-memory simulation, several simplifications were made compared to a production distributed system:

- **Transport Simplification**: Network calls (HTTP/TCP) are mocked as direct synchronous in-memory method invocations. No real sockets or serialization/deserialization occur.
- **Clock Simplification**: Time-based logic, such as cache TTLs (Time-To-Live) and timeouts, are not explicitly modeled in `v1-basic`. Cache entries remain valid until explicitly overwritten or purged.
- **Security Simplification**: Auth/Authz mechanisms (API keys, signed URLs, TLS) are omitted. All requests are assumed to be valid and authorized.
- **Consistency Simplification**: The simulation assumes sequential, synchronous execution for standard fetches and uses an explicit batched `simulateConcurrentFetches` method to test coalescing deterministically without dealing with complex thread-safety, race conditions, or asynchronous locks. Eventual consistency challenges across multiple distributed Edge Nodes are abstracted into single-node sequential logic.
