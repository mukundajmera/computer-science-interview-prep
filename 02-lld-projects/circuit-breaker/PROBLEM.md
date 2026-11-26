# Circuit Breaker

## Problem Statement

Design a Circuit Breaker engine that monitors external service calls, tracks failure rates and slow call rates, and automatically prevents subsequent calls to a failing service to prevent cascading failures.

The system should support a state machine with three main states: `CLOSED`, `OPEN`, and `HALF_OPEN`. When the circuit is closed, calls flow through normally. If the failure rate or slow call rate exceeds a configured threshold within a sliding window (count-based or time-based), the circuit transitions to the `OPEN` state.

In the `OPEN` state, calls are immediately rejected (fast-fail) without invoking the target service. After a configured wait duration, the circuit transitions to the `HALF_OPEN` state, allowing a limited number of test calls to pass through. If these test calls succeed, the circuit resets to `CLOSED`. If they fail, it reverts to `OPEN`.

## Requirements

### Core Requirements
1. **State Machine Management**: Implement the `CLOSED`, `OPEN`, and `HALF_OPEN` states with correct transition logic.
2. **Metric Aggregation**: Support sliding window aggregations to track total calls, failed calls, and slow calls.
3. **Thresholds**: Allow configuring failure rate thresholds and slow call duration thresholds (e.g., failure rate > 50%, or 50% of calls take longer than 1 second).
4. **Fast-Fail Mechanism**: The circuit breaker itself must reject calls quickly when `OPEN` and should not count its own rejections as backend failures.
5. **Fallback Support**: Provide a fallback decorator or mechanism to return default responses when the circuit is `OPEN` or the backend fails.

### Extended Requirements
1. **Time-Based Sliding Window**: Instead of just a fixed count of recent calls, support a rolling time window (e.g., last 10 seconds).
2. **Concurrency**: Ensure that state transitions and metric updates are thread-safe and performant in a multi-threaded environment.
3. **Events & Monitoring**: Emit state transition events and metrics for observability.

### Contract Limitations
1. **Scope Limit**: Version-specific APIs and deterministic fixture inputs/expected outputs are fixed before implementation; no production/security promise is inferred.
