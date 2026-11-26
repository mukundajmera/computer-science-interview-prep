# Webhook Dispatcher - Approach

## Core Patterns
- **Publisher-Subscriber (Pub/Sub):** Manages registrations and routes incoming events to appropriate subscribers.
- **Worker Pool:** A pool of background threads consumes tasks from an internal queue, allowing asynchronous dispatch without blocking publishers.
- **Concurrency Throttling:** Utilizes semaphores on a per-destination (URL/Domain) basis to limit concurrent outbound requests.

## Key Mechanisms
1. **Security (HMAC-SHA256):** Each outgoing request generates a cryptographic hash of the JSON payload using the subscriber's secret. It is sent via `X-Hub-Signature-256`.
2. **Exponential Backoff with Full Jitter:** 
   `sleep = random_between(0, base_delay * 2^attempt)`
   This spreads out retry attempts, reducing load spikes on recovering downstream services.
3. **Dead Letter Queue (DLQ):** A secondary queue or storage mechanism that captures events which failed all delivery attempts.

## Design Decisions
- **In-Memory Concurrency:** To meet the standard library constraint, we will use built-in concurrency primitives (like `Semaphore` and `ExecutorService` in Java, or `threading` and `ThreadPoolExecutor` in Python).
- **Mock HTTP Client:** For the sake of the exercise, HTTP delivery will be simulated or abstracted behind an interface that can throw exceptions, return 500s, or return 200s to test backoff and fast-path behavior.
