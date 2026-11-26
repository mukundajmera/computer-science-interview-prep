# Strong Answer: Webhook Dispatcher System

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the Webhook Dispatcher System, I will focus on modeling the core entities, defining the interfaces, and ensuring thread-safe operations under high concurrency. Our primary goal is to ensure reliable delivery, isolation between endpoints, and fault tolerance."

By establishing these constraints early, we frame the discussion around concrete engineering trade-offs. The high-level requirements dictate a system capable of handling substantial load while protecting both our internal workers and external destination endpoints.

## 2. Entity Modeling, APIs & Feature Deltas (5-15 minutes)

**Say:** "Let's discuss the entity modeling. The core public API revolves around the `WebhookDispatcher`, providing `addSubscriber(Subscriber)` and `publish(Event)`. The main entities are:
- **Event**: Encapsulates a `topic` and a dictionary/map `payload`.
- **Subscriber**: Defines the target endpoint, HMAC `secret`, and `topicRegex` filter.
- **WebhookTask**: Represents a delivery attempt with its current retry count.
- **HttpClient**: Abstract interface for outbound calls.
- **PersistentDlq**: A bounded dead-letter queue.
- **CircuitBreaker**: Prevents overwhelming failing endpoints.

In the v3-optimized version (compared to v1), we introduced dynamic concurrent host limits via `Semaphore` arrays and state-based `CircuitBreaker` instances per destination to protect external systems."

## 3. Design Pattern Justifications & Acceptance Criteria (15-25 minutes)

**Say:** "The design addresses the core use cases explicitly:
- **Normal use-case**: An event published matches a subscriber's regex. A task is queued, picked up by the `workerPool`, signed via HMAC-SHA256, and delivered.
- **Empty/invalid input**: If an event doesn't match any subscriber's regex (e.g., `testNoMatchTopic`), it's efficiently dropped with zero outbound calls.
- **Duplicate operation**: While network retries mean 'at-least-once' delivery, the system relies on idempotency at the destination (e.g., using `order_id` in the payload) to safely handle retries.

This satisfies our core contract in both Java 11+ and Python 3.8+ versions."

## 4. Thread-Safety, Capacity Boundaries & Scale (25-35 minutes)

**Say:** "Handling concurrency is critical. We use a fixed `ExecutorService` (worker pool) and a `ScheduledExecutorService` (retry scheduler) in Java, and `threading` with bounded queues in Python. The capacity boundaries are explicitly managed:
- **Per-Destination Limits**: We limit concurrent requests to a single host using a `Semaphore`. Threads block (or yield) when attempting to acquire a permit, preventing connection exhaustion.
- **Worker Pool Limit**: Bound our own CPU/Memory by a maximum number of worker threads.
- **DLQ Boundary**: The `PersistentDlq` has a strict capacity limit (e.g., 7) to prevent unbounded memory growth."

## 5. Failure Rollback & Concurrency Trace (35-45 minutes)

**Say:** "Let's trace a concrete failure scenario: An endpoint starts returning HTTP 500.
1. The worker thread executes the HTTP post and receives a 500.
2. The task's attempt counter increments. If it exceeds max retries, it is routed to the `PersistentDlq`.
3. If it hasn't exceeded the max, a backoff delay is calculated (exponential).
4. Simultaneously, the `CircuitBreaker` for that endpoint tracks the failure. After consecutive failures, it trips to OPEN.
5. While OPEN, any task trying to acquire a connection immediately fails and moves to retry, saving the outbound network call and protecting the failing host."

This prevents "thundering herd" issues and guarantees bounded resource usage during widespread external failures.
